#!/usr/bin/env python3
"""
LSTM Fiyat Tahmin Modeli Entegrasyon Örneği

Bu dosya, mevcut trading botunuza LSTM fiyat tahmin modelini nasıl entegre 
edeceğinizi gösteren bir örnektir.
"""

import asyncio
import logging
from datetime import datetime
from binance.client import Client
import pandas as pd

# ML modüllerini import et
from ml_models import LSTMPricePredictor, ModelTrainer, DataPreprocessor
import config

# Logger ayarla
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LSTMTradingBot:
    """
    LSTM tahmin modeli ile güçlendirilmiş trading bot
    """
    
    def __init__(self):
        # Binance client
        self.client = Client(config.API_KEY, config.API_SECRET)
        
        # LSTM model trainer
        self.model_trainer = ModelTrainer(self.client)
        
        # Aktif coin listesi
        self.active_coins = []
        
        # LSTM tahminleri cache
        self.predictions_cache = {}
        
        logger.info("LSTM Trading Bot başlatıldı")
    
    async def initialize_models(self):
        """
        Modelleri başlat - kayıtlı modelleri yükle veya eğit
        """
        logger.info("LSTM modelleri başlatılıyor...")
        
        # Coin listesini yükle
        with open(config.COIN_LIST_FILE, 'r') as f:
            import json
            coin_data = json.load(f)
            self.active_coins = [coin['symbol'] for coin in coin_data]
        
        # Mevcut modelleri yükle
        loaded_count = self.model_trainer.load_existing_models()
        
        if loaded_count == 0:
            logger.info("Hiç model bulunamadı, yeni modeller eğitiliyor...")
            await self.train_all_models()
        else:
            logger.info(f"{loaded_count} model yüklendi")
            
            # Modelleri güncelleme gerekiyor mu kontrol et
            await self.check_model_updates()
    
    async def train_all_models(self):
        """
        Tüm coinler için LSTM modellerini eğit
        """
        if not config.LSTM_ENABLED:
            logger.info("LSTM devre dışı")
            return
        
        logger.info(f"{len(self.active_coins)} coin için model eğitimi başlatılıyor...")
        
        # Eğitimi paralel olarak yapabilirsin ama API limit'i için sırayla yapalım
        results = self.model_trainer.train_all_models(self.active_coins)
        
        success_count = sum(results.values())
        logger.info(f"Model eğitimi tamamlandı: {success_count}/{len(self.active_coins)}")
        
        return results
    
    async def check_model_updates(self):
        """
        Modellerin güncellenme ihtiyacını kontrol et
        """
        for symbol in self.active_coins:
            if self.model_trainer.retrain_model_if_needed(
                symbol, config.LSTM_RETRAIN_INTERVAL_HOURS
            ):
                logger.info(f"{symbol} modeli güncellendi")
    
    async def get_lstm_signal(self, symbol: str, current_data: pd.DataFrame) -> dict:
        """
        Belirli bir coin için LSTM sinyali al
        """
        if not config.LSTM_ENABLED:
            return {'score': 0, 'direction': 'NEUTRAL', 'confidence': 0}
        
        try:
            # LSTM tahminini al
            prediction = self.model_trainer.get_prediction(
                symbol, config.LSTM_PREDICTION_STEPS
            )
            
            if not prediction:
                return {'score': 0, 'direction': 'NEUTRAL', 'confidence': 0}
            
            # Cache'e kaydet
            self.predictions_cache[symbol] = prediction
            
            # Mevcut fiyat ve tahmin edilen fiyatları karşılaştır
            current_price = prediction['current_price']
            next_predictions = prediction['predictions']
            model_confidence = prediction['model_confidence']
            
            # Sinyal hesapla
            if len(next_predictions) > 0:
                # Kısa vadeli tahmin (1 adım sonrası)
                next_price = next_predictions[0]
                price_change_percent = ((next_price - current_price) / current_price) * 100
                
                # Uzun vadeli trend (tüm tahminler)
                if len(next_predictions) >= 2:
                    long_term_trend = (next_predictions[-1] - current_price) / current_price * 100
                else:
                    long_term_trend = price_change_percent
                
                # Sinyal yönü ve gücü
                if price_change_percent > 1.0:  # %1'den fazla yükseliş
                    direction = 'LONG'
                    signal_strength = min(abs(price_change_percent) * 10, 100)
                elif price_change_percent < -1.0:  # %1'den fazla düşüş
                    direction = 'SHORT'
                    signal_strength = min(abs(price_change_percent) * 10, 100)
                else:
                    direction = 'NEUTRAL'
                    signal_strength = 0
                
                # Model güvenini dahil et
                final_score = signal_strength * model_confidence
                
                # Minimum eşiği kontrol et
                if model_confidence < config.LSTM_MIN_CONFIDENCE:
                    final_score = 0
                    direction = 'NEUTRAL'
                
                return {
                    'score': final_score,
                    'direction': direction,
                    'confidence': model_confidence,
                    'price_change_percent': price_change_percent,
                    'predicted_price': next_price,
                    'long_term_trend': long_term_trend,
                    'predictions': next_predictions
                }
            
        except Exception as e:
            logger.error(f"{symbol} LSTM sinyal hatası: {e}")
        
        return {'score': 0, 'direction': 'NEUTRAL', 'confidence': 0}
    
    def integrate_lstm_with_existing_signals(self, symbol: str, 
                                           existing_score: float,
                                           lstm_signal: dict) -> float:
        """
        LSTM sinyalini mevcut sinyal sistemiyle entegre et
        """
        if not config.LSTM_ENABLED or lstm_signal['score'] == 0:
            return existing_score
        
        # LSTM ağırlığını uygula
        lstm_contribution = lstm_signal['score'] * config.LSTM_PREDICTION_WEIGHT
        
        # Sinyal yönleri uyumlu mu kontrol et
        if existing_score > 50 and lstm_signal['direction'] == 'LONG':
            # Aynı yönde güçlendirme
            enhanced_score = existing_score + lstm_contribution
        elif existing_score < 50 and lstm_signal['direction'] == 'SHORT':
            # Aynı yönde güçlendirme  
            enhanced_score = existing_score - lstm_contribution
        else:
            # Farklı yönlerde - daha konservatif yaklaşım
            enhanced_score = existing_score * (1 - config.LSTM_PREDICTION_WEIGHT * 0.5)
        
        # Sınırlara dahil et
        enhanced_score = max(0, min(100, enhanced_score))
        
        logger.debug(f"{symbol}: Orijinal skor {existing_score:.2f}, "
                    f"LSTM katkısı {lstm_contribution:.2f}, "
                    f"Final skor {enhanced_score:.2f}")
        
        return enhanced_score
    
    async def get_lstm_price_targets(self, symbol: str) -> dict:
        """
        LSTM tahminlerine göre fiyat hedeflerini hesapla
        """
        if symbol not in self.predictions_cache:
            return {}
        
        prediction = self.predictions_cache[symbol]
        current_price = prediction['current_price']
        predictions = prediction['predictions']
        
        if not predictions:
            return {}
        
        # Take profit ve stop loss seviyelerini hesapla
        max_predicted = max(predictions)
        min_predicted = min(predictions)
        
        # LSTM bazlı hedefler
        lstm_targets = {
            'take_profit_price': max_predicted,
            'stop_loss_price': min_predicted,
            'confidence': prediction['confidence'],
            'prediction_horizon': len(predictions)
        }
        
        return lstm_targets
    
    async def send_lstm_notification(self, symbol: str, prediction: dict):
        """
        LSTM tahmin bildirimini gönder
        """
        if not config.NOTIFY_LSTM_PREDICTIONS:
            return
        
        try:
            current_price = prediction['current_price']
            next_price = prediction['predictions'][0] if prediction['predictions'] else current_price
            confidence = prediction['confidence']
            
            change_percent = ((next_price - current_price) / current_price) * 100
            
            message = f"""
🧠 LSTM Fiyat Tahmini
💰 {symbol}
📈 Mevcut: ${current_price:.4f}
🔮 Tahmin: ${next_price:.4f}
📊 Değişim: {change_percent:+.2f}%
🎯 Güven: {confidence:.1%}
⏰ {datetime.now().strftime('%H:%M:%S')}
"""
            
            # Telegram'a gönder (mevcut telegram fonksiyonunu kullan)
            # await self.send_telegram_message(message)
            logger.info(f"LSTM bildirimi: {symbol} {change_percent:+.2f}%")
            
        except Exception as e:
            logger.error(f"LSTM bildirim hatası: {e}")

# Ana bot entegrasyonu için örnek fonksiyon
async def enhanced_signal_calculation(symbol: str, market_data: pd.DataFrame, 
                                    lstm_bot: LSTMTradingBot) -> float:
    """
    Mevcut sinyal hesaplamasına LSTM entegrasyonu örneği
    Bu fonksiyonu main.py'daki mevcut sinyal hesaplama fonksiyonunuza adapte edin
    """
    
    # 1. Mevcut teknik analiz sinyallerini hesapla (RSI, Bollinger, vb.)
    # existing_score = calculate_technical_signals(market_data)  # Mevcut fonksiyonunuz
    existing_score = 75.0  # Örnek değer
    
    # 2. LSTM sinyalini al
    lstm_signal = await lstm_bot.get_lstm_signal(symbol, market_data)
    
    # 3. LSTM ile entegre et
    final_score = lstm_bot.integrate_lstm_with_existing_signals(
        symbol, existing_score, lstm_signal
    )
    
    # 4. LSTM bildirimini gönder
    if lstm_signal['score'] > 0:
        await lstm_bot.send_lstm_notification(symbol, lstm_bot.predictions_cache.get(symbol, {}))
    
    return final_score

# Test fonksiyonu
async def test_lstm_integration():
    """
    LSTM entegrasyonunu test et
    """
    bot = LSTMTradingBot()
    
    try:
        # Modelleri başlat
        await bot.initialize_models()
        
        # Test coin'i için tahmin al
        test_symbol = "BTCUSDT"
        
        # Son 200 saatlik veri al
        recent_data = bot.model_trainer.fetch_training_data(test_symbol, limit=200)
        
        if not recent_data.empty:
            # LSTM sinyali al
            lstm_signal = await bot.get_lstm_signal(test_symbol, recent_data)
            
            print(f"\n{test_symbol} LSTM Sinyali:")
            print(f"Skor: {lstm_signal['score']:.2f}")
            print(f"Yön: {lstm_signal['direction']}")
            print(f"Güven: {lstm_signal['confidence']:.2%}")
            
            if 'predicted_price' in lstm_signal:
                print(f"Tahmin edilen fiyat: ${lstm_signal['predicted_price']:.2f}")
                print(f"Beklenen değişim: {lstm_signal['price_change_percent']:+.2f}%")
        
    except Exception as e:
        logger.error(f"Test hatası: {e}")

if __name__ == "__main__":
    # Test çalıştır
    asyncio.run(test_lstm_integration()) 