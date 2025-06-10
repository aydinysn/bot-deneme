#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ccxt
import pandas as pd
import numpy as np
import time
import json
import logging
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional, Tuple
import threading
from collections import defaultdict

# Local imports
try:
    from config import *
except ImportError:
    # Fallback konfigürasyon
    API_KEY = "your_binance_api_key"
    API_SECRET = "your_binance_api_secret"
    TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
    TELEGRAM_CHAT_ID = "your_telegram_chat_id"
    LARGE_TRADE_THRESHOLD = 100000
    WHALE_THRESHOLD = 500000
    MEGA_WHALE_THRESHOLD = 1000000
    MONITORING_SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'SOL/USDT']
    SCAN_INTERVAL = 30
    API_DELAY = 2

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whale_positions.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhalePositionTracker:
    def __init__(self, api_key: str = None, api_secret: str = None, 
                 telegram_token: str = None, telegram_chat_id: str = None):
        """
        Balina pozisyon takip sistemi
        
        Args:
            api_key: Binance API anahtarı
            api_secret: Binance API gizli anahtarı
            telegram_token: Telegram bot token (opsiyonel)
            telegram_chat_id: Telegram chat ID (opsiyonel)
        """
        # Config'den değerleri al veya parametre kullan
        self.api_key = api_key or API_KEY
        self.api_secret = api_secret or API_SECRET
        self.telegram_token = telegram_token or TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = telegram_chat_id or TELEGRAM_CHAT_ID
        
        self.exchange = self._init_exchange()
        
        # Takip edilen veriler
        self.tracked_positions = {}
        self.recent_whale_trades = []
        self.whale_statistics = defaultdict(dict)
        self.alert_cooldowns = {}  # Son alert zamanları
        
        self.is_running = False
        
    def _init_exchange(self):
        """Binance exchange bağlantısını başlatır (Public API)"""
        try:
            exchange = ccxt.binance({
                'sandbox': False,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future'  # Futures market
                }
            })
            # load_markets() private API gerektiriyor, public API için gerekli değil
            logger.info("Binance Public API bağlantısı başarıyla kuruldu")
            return exchange
        except Exception as e:
            logger.error(f"Exchange bağlantı hatası: {e}")
            raise
    
    def send_telegram_message(self, message: str):
        """Telegram üzerinden mesaj gönderir"""
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram bilgileri eksik, mesaj gönderilemiyor")
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data)
            if response.status_code != 200:
                logger.error(f"Telegram mesaj gönderme hatası: {response.text}")
        except Exception as e:
            logger.error(f"Telegram hatası: {e}")
    
    def analyze_large_trades(self, symbol: str, limit: int = None) -> List[Dict]:
        """
        Büyük işlemleri analiz eder ve balina aktivitesini tespit eder
        """
        limit = limit or getattr(globals(), 'TRADES_LIMIT', 500)
        
        try:
            # Futures trades verilerini al
            trades = self.exchange.fetch_trades(symbol, limit=limit)
            current_price = self.exchange.fetch_ticker(symbol)['last']
            
            large_trades = []
            
            for trade in trades:
                trade_value = trade['amount'] * trade['price']
                
                if trade_value >= LARGE_TRADE_THRESHOLD:
                    # Pozisyon yönünü tahmin et
                    position_side = self._determine_position_side(trade, current_price)
                    whale_type = self._classify_whale_size(trade_value)
                    
                    trade_info = {
                        'symbol': symbol,
                        'timestamp': trade['timestamp'],
                        'datetime': datetime.fromtimestamp(trade['timestamp'] / 1000),
                        'side': trade['side'],
                        'amount': trade['amount'],
                        'price': trade['price'],
                        'value': trade_value,
                        'whale_type': whale_type,
                        'position_side': position_side,
                        'trade_id': trade['id']
                    }
                    
                    large_trades.append(trade_info)
            
            return large_trades
            
        except Exception as e:
            logger.error(f"Büyük işlem analizi hatası ({symbol}): {e}")
            return []
    
    def _determine_position_side(self, trade: Dict, current_price: float) -> str:
        """Trade verisinden pozisyon yönünü tahmin eder"""
        price_diff_percent = abs(trade['price'] - current_price) / current_price * 100
        
        if price_diff_percent <= 0.1:  # %0.1 içinde
            return 'LONG' if trade['side'] == 'buy' else 'SHORT'
        else:
            return 'UNKNOWN'
    
    def _classify_whale_size(self, trade_value: float) -> str:
        """İşlem değerine göre balina tipini sınıflandırır"""
        if trade_value >= MEGA_WHALE_THRESHOLD:
            return 'MEGA_WHALE'
        elif trade_value >= WHALE_THRESHOLD:
            return 'WHALE'
        else:
            return 'LARGE_TRADER'
    
    def detect_whale_positions(self, symbol: str) -> List[Dict]:
        """Belirli bir coin için balina pozisyonlarını tespit eder"""
        try:
            # Son büyük işlemleri al
            large_trades = self.analyze_large_trades(symbol)
            
            # Son 1 saat içindeki işlemleri filtrele
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_trades = [
                trade for trade in large_trades 
                if trade['datetime'] >= one_hour_ago
            ]
            
            # Pozisyon analizini grup halinde yap
            position_analysis = self._analyze_position_flow(recent_trades)
            
            return position_analysis
            
        except Exception as e:
            logger.error(f"Balina pozisyon tespiti hatası ({symbol}): {e}")
            return []
    
    def _analyze_position_flow(self, trades: List[Dict]) -> List[Dict]:
        """İşlem akışından pozisyon yönünü analiz eder"""
        if not trades:
            return []
        
        analysis_results = []
        symbol_trades = defaultdict(list)
        
        for trade in trades:
            symbol_trades[trade['symbol']].append(trade)
        
        for symbol, symbol_trades_list in symbol_trades.items():
            # Long ve short işlemleri ayır
            long_trades = [t for t in symbol_trades_list if t['position_side'] == 'LONG']
            short_trades = [t for t in symbol_trades_list if t['position_side'] == 'SHORT']
            
            long_volume = sum(t['value'] for t in long_trades)
            short_volume = sum(t['value'] for t in short_trades)
            total_volume = long_volume + short_volume
            
            if total_volume >= LARGE_TRADE_THRESHOLD:
                # Dominant yön belirle
                if long_volume > short_volume * 1.5:
                    dominant_side = 'LONG'
                    confidence = long_volume / total_volume
                elif short_volume > long_volume * 1.5:
                    dominant_side = 'SHORT'
                    confidence = short_volume / total_volume
                else:
                    dominant_side = 'NEUTRAL'
                    confidence = 0.5
                
                analysis = {
                    'symbol': symbol,
                    'timestamp': datetime.now(),
                    'dominant_side': dominant_side,
                    'confidence': confidence,
                    'long_volume': long_volume,
                    'short_volume': short_volume,
                    'total_volume': total_volume,
                    'trade_count': len(symbol_trades_list),
                    'largest_trade': max(symbol_trades_list, key=lambda x: x['value']),
                    'whale_activity_level': self._calculate_whale_activity_level(symbol_trades_list)
                }
                
                analysis_results.append(analysis)
        
        return analysis_results
    
    def _calculate_whale_activity_level(self, trades: List[Dict]) -> str:
        """Balina aktivite seviyesini hesaplar"""
        total_value = sum(t['value'] for t in trades)
        whale_count = len([t for t in trades if t['whale_type'] in ['WHALE', 'MEGA_WHALE']])
        
        if total_value >= MEGA_WHALE_THRESHOLD * 3 or whale_count >= 5:
            return 'EXTREME'
        elif total_value >= WHALE_THRESHOLD * 2 or whale_count >= 3:
            return 'HIGH'
        elif total_value >= WHALE_THRESHOLD or whale_count >= 1:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def monitor_whale_positions(self):
        """Tüm coinler için balina pozisyonlarını sürekli takip eder"""
        logger.info("Balina pozisyon takibi başlatıldı...")
        self.is_running = True
        
        while self.is_running:
            try:
                for symbol in MONITORING_SYMBOLS:
                    try:
                        # Balina pozisyonlarını tespit et
                        position_analysis = self.detect_whale_positions(symbol)
                        
                        for analysis in position_analysis:
                            # Önemli aktiviteleri bildir
                            if self._should_alert(analysis):
                                self._send_position_alert(analysis)
                                
                            # İstatistikleri güncelle
                            self._update_statistics(analysis)
                        
                        # API rate limit için bekleme
                        time.sleep(API_DELAY)
                        
                    except Exception as e:
                        logger.error(f"Monitoring hatası ({symbol}): {e}")
                        continue
                
                # Döngü arası bekleme
                logger.info(f"Balina tarama turu tamamlandı. {SCAN_INTERVAL} saniye bekleniyor...")
                time.sleep(SCAN_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Balina takibi durduruldu.")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Ana döngü hatası: {e}")
                time.sleep(10)
    
    def _should_alert(self, analysis: Dict) -> bool:
        """Bildirim gönderilip gönderilmeyeceğini belirler"""
        symbol = analysis['symbol']
        current_time = time.time()
        
        # Cooldown kontrolü
        cooldown_key = f"{symbol}_{analysis['dominant_side']}"
        if cooldown_key in self.alert_cooldowns:
            if current_time - self.alert_cooldowns[cooldown_key] < getattr(globals(), 'ALERT_COOLDOWN', 300):
                return False
        
        # Alert kriterleri
        activity_levels = getattr(globals(), 'ALERT_ACTIVITY_LEVELS', ['HIGH', 'EXTREME'])
        confidence_threshold = getattr(globals(), 'ALERT_CONFIDENCE_THRESHOLD', 0.7)
        
        should_alert = (
            analysis['whale_activity_level'] in activity_levels and
            analysis['total_volume'] >= WHALE_THRESHOLD and
            analysis['confidence'] >= confidence_threshold
        )
        
        if should_alert:
            self.alert_cooldowns[cooldown_key] = current_time
        
        return should_alert
    
    def _send_position_alert(self, analysis: Dict):
        """Balina pozisyon bildirimini gönderir"""
        symbol = analysis['symbol']
        side = analysis['dominant_side']
        volume = analysis['total_volume']
        confidence = analysis['confidence']
        activity_level = analysis['whale_activity_level']
        largest_trade = analysis['largest_trade']
        
        # Emoji ve renk seçimi
        side_emoji = "🟢" if side == 'LONG' else "🔴" if side == 'SHORT' else "🟡"
        activity_emoji = "🚨" if activity_level == 'EXTREME' else "⚠️" if activity_level == 'HIGH' else "📊"
        
        message = (
            f"{activity_emoji} <b>BALİNA POZİSYON TESPİTİ</b>\n\n"
            f"🪙 <b>Coin:</b> {symbol}\n"
            f"{side_emoji} <b>Pozisyon:</b> {side}\n"
            f"💰 <b>Toplam Hacim:</b> ${volume:,.0f}\n"
            f"📊 <b>Güven:</b> {confidence:.1%}\n"
            f"🔥 <b>Aktivite:</b> {activity_level}\n"
            f"📈 <b>İşlem Sayısı:</b> {analysis['trade_count']}\n\n"
            f"💎 <b>En Büyük İşlem:</b>\n"
            f"└ Değer: ${largest_trade['value']:,.0f}\n"
            f"└ Tip: {largest_trade['whale_type']}\n"
            f"└ Zaman: {largest_trade['datetime'].strftime('%H:%M:%S')}\n\n"
            f"⏰ <b>Tespit Zamanı:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        
        self.send_telegram_message(message)
        logger.info(f"Balina pozisyon bildirimi gönderildi: {symbol} - {side}")
    
    def _update_statistics(self, analysis: Dict):
        """Balina istatistiklerini günceller"""
        symbol = analysis['symbol']
        current_time = datetime.now()
        
        if symbol not in self.whale_statistics:
            self.whale_statistics[symbol] = {
                'total_volume_24h': 0,
                'long_volume_24h': 0,
                'short_volume_24h': 0,
                'trade_count_24h': 0,
                'last_update': current_time,
                'positions_history': []
            }
        
        stats = self.whale_statistics[symbol]
        
        # 24 saatlik istatistikleri güncelle
        stats['total_volume_24h'] += analysis['total_volume']
        stats['long_volume_24h'] += analysis['long_volume']
        stats['short_volume_24h'] += analysis['short_volume']
        stats['trade_count_24h'] += analysis['trade_count']
        stats['last_update'] = current_time
        
        # Pozisyon geçmişine ekle
        stats['positions_history'].append({
            'timestamp': current_time,
            'side': analysis['dominant_side'],
            'volume': analysis['total_volume'],
            'confidence': analysis['confidence']
        })
        
        # Eski verileri temizle
        retention_hours = getattr(globals(), 'DATA_RETENTION_HOURS', 24)
        cutoff_time = current_time - timedelta(hours=retention_hours)
        stats['positions_history'] = [
            pos for pos in stats['positions_history']
            if pos['timestamp'] >= cutoff_time
        ]
    
    def get_whale_summary(self) -> Dict:
        """Balina aktivitelerinin özetini döner"""
        summary = {
            'timestamp': datetime.now(),
            'total_monitored_coins': len(MONITORING_SYMBOLS),
            'active_coins': len(self.whale_statistics),
            'top_whale_coins': [],
            'overall_sentiment': 'NEUTRAL'
        }
        
        # En aktif coinleri sırala
        sorted_coins = sorted(
            self.whale_statistics.items(),
            key=lambda x: x[1]['total_volume_24h'],
            reverse=True
        )
        
        for symbol, stats in sorted_coins[:5]:
            long_ratio = stats['long_volume_24h'] / (stats['total_volume_24h'] or 1)
            
            summary['top_whale_coins'].append({
                'symbol': symbol,
                'total_volume': stats['total_volume_24h'],
                'long_ratio': long_ratio,
                'trade_count': stats['trade_count_24h'],
                'dominant_side': 'LONG' if long_ratio > 0.6 else 'SHORT' if long_ratio < 0.4 else 'NEUTRAL'
            })
        
        # Genel sentiment hesapla
        if summary['top_whale_coins']:
            long_coins = sum(1 for coin in summary['top_whale_coins'] if coin['dominant_side'] == 'LONG')
            short_coins = sum(1 for coin in summary['top_whale_coins'] if coin['dominant_side'] == 'SHORT')
            
            if long_coins > short_coins * 1.5:
                summary['overall_sentiment'] = 'BULLISH'
            elif short_coins > long_coins * 1.5:
                summary['overall_sentiment'] = 'BEARISH'
        
        return summary
    
    def send_daily_summary(self):
        """Günlük balina aktivite özetini gönderir"""
        summary = self.get_whale_summary()
        
        sentiment_emoji = "🚀" if summary['overall_sentiment'] == 'BULLISH' else "📉" if summary['overall_sentiment'] == 'BEARISH' else "⚖️"
        
        message = (
            f"{sentiment_emoji} <b>GÜNLÜK BALİNA ÖZETİ</b>\n\n"
            f"📊 <b>Genel Sentiment:</b> {summary['overall_sentiment']}\n"
            f"🪙 <b>Aktif Coin:</b> {summary['active_coins']}/{summary['total_monitored_coins']}\n\n"
            f"<b>🏆 TOP 5 BALİNA AKTİVİTESİ:</b>\n"
        )
        
        for i, coin in enumerate(summary['top_whale_coins'], 1):
            side_emoji = "🟢" if coin['dominant_side'] == 'LONG' else "🔴" if coin['dominant_side'] == 'SHORT' else "🟡"
            message += (
                f"{i}. {side_emoji} <b>{coin['symbol']}</b>\n"
                f"   💰 ${coin['total_volume']:,.0f} | "
                f"📊 {coin['trade_count']} işlem\n"
            )
        
        message += f"\n⏰ <b>Rapor Zamanı:</b> {summary['timestamp'].strftime('%d/%m/%Y %H:%M')}"
        
        self.send_telegram_message(message)
        logger.info("Günlük balina özeti gönderildi")
    
    def stop_monitoring(self):
        """Takibi durdurur"""
        self.is_running = False
        logger.info("Balina takibi durdurma sinyali gönderildi")

def main():
    """Ana fonksiyon"""
    # Tracker'ı başlat
    tracker = WhalePositionTracker()
    
    try:
        # Başlangıç bildirimi
        tracker.send_telegram_message(
            "🐋 <b>BALİNA POZİSYON TAKİBİ BAŞLATILDI</b>\n\n"
            f"📊 <b>Takip Edilen Coin:</b> {len(MONITORING_SYMBOLS)}\n"
            f"💰 <b>Minimum Limit:</b> ${LARGE_TRADE_THRESHOLD:,}\n"
            f"🐋 <b>Balina Limiti:</b> ${WHALE_THRESHOLD:,}\n"
            f"⏰ <b>Başlangıç:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
        
        # Takibi başlat
        tracker.monitor_whale_positions()
        
    except KeyboardInterrupt:
        logger.info("Kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
    finally:
        tracker.stop_monitoring()

if __name__ == "__main__":
    main()
