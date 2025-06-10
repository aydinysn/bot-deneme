#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐋 Simple Whale Position Tracker
Basit ama etkili whale position tracker
"""

import ccxt
import time
import logging
import requests
from datetime import datetime

# Configuration
LARGE_TRADE_THRESHOLD = 100000      # $100K minimum işlem büyüklüğü
WHALE_THRESHOLD = 500000            # $500K balina limiti
MEGA_WHALE_THRESHOLD = 1000000      # $1M mega balina limiti
SCAN_INTERVAL = 30                  # Tarama aralığı (saniye)
API_DELAY = 2                       # API çağrıları arası bekleme (saniye)
ALERT_COOLDOWN = 300                # Aynı coin için alert arası minimum süre (saniye)

# Telegram bilgileri
TELEGRAM_BOT_TOKEN = "7653317241:AAH2t8-C4qBtzi9-zEnFF9mJ0csCFJ8iyVA"
TELEGRAM_CHAT_ID = "924928056"

MONITORING_SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'SOL/USDT',
    'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT'
]

print(f"🚀 Simple Whale Position Tracker başlatılıyor...")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_whale_positions.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleWhaleTracker:
    def __init__(self):
        self.exchange = None
        self.last_alerts = {}
        self._initialize_exchange()
        
    def _initialize_exchange(self):
        try:
            # Sadece public API kullan
            self.exchange = ccxt.binance({
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })
            
            # Bağlantı testi
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            logger.info(f"📊 BTC Fiyat: ${ticker['last']:,.2f}")
            logger.info("✅ Binance Public API bağlantısı başarılı")
            
        except Exception as e:
            logger.error(f"❌ Exchange bağlantı hatası: {e}")
            raise
    
    def send_telegram_message(self, message: str) -> bool:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Telegram mesaj hatası: {e}")
            return False
    
    def analyze_symbol(self, symbol: str):
        try:
            logger.info(f"🔍 {symbol} analiz ediliyor...")
            
            # Son işlemleri al
            trades = self.exchange.fetch_trades(symbol, limit=100)
            
            large_trades = []
            for trade in trades:
                value = trade['amount'] * trade['price']
                if value >= LARGE_TRADE_THRESHOLD:
                    large_trades.append({
                        'value': value,
                        'side': trade['side'],
                        'time': datetime.fromtimestamp(trade['timestamp'] / 1000)
                    })
            
            if large_trades:
                # Buy/Sell analizi
                buy_volume = sum(t['value'] for t in large_trades if t['side'] == 'buy')
                sell_volume = sum(t['value'] for t in large_trades if t['side'] == 'sell')
                total_volume = buy_volume + sell_volume
                
                # Dominant side
                if buy_volume > sell_volume * 1.5:
                    dominant_side = "LONG"
                    confidence = buy_volume / total_volume
                elif sell_volume > buy_volume * 1.5:
                    dominant_side = "SHORT"
                    confidence = sell_volume / total_volume
                else:
                    dominant_side = "NEUTRAL"
                    confidence = 0.5
                
                # Alert gönder
                if total_volume >= WHALE_THRESHOLD and confidence >= 0.7:
                    current_time = time.time()
                    last_alert = self.last_alerts.get(symbol, 0)
                    
                    if current_time - last_alert >= ALERT_COOLDOWN:  # 5 dakika cooldown
                        whale_emoji = "🐋" if total_volume >= MEGA_WHALE_THRESHOLD else "🐟"
                        side_emoji = "🟢" if dominant_side == "LONG" else "🔴" if dominant_side == "SHORT" else "🟡"
                        
                        message = f"""{whale_emoji} <b>BALİNA TESPİTİ</b>

🪙 <b>Coin:</b> {symbol}
{side_emoji} <b>Pozisyon:</b> {dominant_side}
💰 <b>Toplam Hacim:</b> ${total_volume:,.0f}
📊 <b>Güven:</b> {confidence:.1%}
📈 <b>İşlem Sayısı:</b> {len(large_trades)}

⏰ <b>Zaman:</b> {datetime.now().strftime('%H:%M:%S')}"""
                        
                        if self.send_telegram_message(message):
                            self.last_alerts[symbol] = current_time
                            logger.info(f"📢 {symbol} alert gönderildi!")
                
                logger.info(f"📊 {symbol}: {dominant_side} - ${total_volume:,.0f} (Güven: {confidence:.1%})")
            else:
                logger.info(f"ℹ️ {symbol}: Büyük işlem tespit edilmedi")
            
        except Exception as e:
            logger.error(f"{symbol} analiz hatası: {e}")
    
    def start_monitoring(self):
        logger.info("🚀 Monitoring başlatılıyor...")
        
        start_message = f"""🚀 <b>SIMPLE WHALE TRACKER BAŞLATILDI</b>

📊 <b>Takip Edilen Coinler:</b> {len(MONITORING_SYMBOLS)}
💰 <b>Minimum İşlem:</b> ${LARGE_TRADE_THRESHOLD:,}
🐋 <b>Balina Limiti:</b> ${WHALE_THRESHOLD:,}
⏱️ <b>Tarama Aralığı:</b> {SCAN_INTERVAL}s

✅ <b>Sistem aktif!</b>"""
        
        self.send_telegram_message(start_message)
        
        cycle = 0
        
        try:
            while True:
                cycle += 1
                logger.info(f"🔄 Döngü #{cycle} başlıyor...")
                
                for symbol in MONITORING_SYMBOLS:
                    self.analyze_symbol(symbol)
                    time.sleep(API_DELAY)
                
                logger.info(f"✅ Döngü #{cycle} tamamlandı")
                logger.info(f"😴 {SCAN_INTERVAL}s bekleniyor...")
                time.sleep(SCAN_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("🛑 Kullanıcı tarafından durduruldu")
            self.send_telegram_message("🛑 <b>Simple Whale Tracker durduruldu</b>")
        except Exception as e:
            logger.error(f"❌ Kritik hata: {e}")
            self.send_telegram_message(f"❌ <b>Simple Whale Tracker HATA!</b>\n\n{str(e)}")

def main():
    try:
        print("🐋 Simple Whale Position Tracker v1.0")
        print("=" * 50)
        
        tracker = SimpleWhaleTracker()
        tracker.start_monitoring()
        
    except Exception as e:
        logger.error(f"Program hatası: {e}")
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    main() 