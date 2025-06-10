#!/usr/bin/env python3
"""
ML Fiyat Tahmin Modeli Entegrasyon Örneği (Python 3.13 Uyumlu)

Bu dosya, mevcut trading botunuza ML fiyat tahmin modelini nasıl entegre 
edeceğinizi gösteren bir örnektir. TensorFlow olmadan çalışır.
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# Parent dizini path'e ekle (config.py için)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.client import Client
import pandas as pd

# ML modüllerini import et
from ml_models import MLPricePredictor, ModelTrainer, DataPreprocessor
import config

# Logger ayarla
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLTradingBot:
    """
    ML tahmin modeli ile güçlendirilmiş trading bot
    Python 3.13 uyumlu, TensorFlow gerektirmez
    """
    
    def __init__(self):
        # Binance client
        self.client = Client(config.API_KEY, config.API_SECRET)
        
        # ML model trainer
        self.model_trainer = ModelTrainer(self.client)
        
        # Aktif coin listesi
        self.active_coins = []
        
        # ML tahminleri cache
        self.predictions_cache = {}
        
        logger.info("ML Trading Bot başlatıldı (Python 3.13 uyumlu)")
    
    async def initialize_models(self):
        """
        Modelleri başlat - kayıtlı modelleri yükle veya eğit
        """
        logger.info("ML modelleri başlatılıyor...")
        
        # Coin listesini yükle
        with open(config.COIN_LIST_FILE, 'r') as f:
            import json
            coin_data = json.load(f)
            # Format düzeltmesi - Binance formatına çevir
            if 'coins' in coin_data:
                self.active_coins = [coin.replace('/', '') for coin in coin_data['coins'][:5]]  # İlk 5 coin ile test
            else:
                self.active_coins = [coin['symbol'] for coin in coin_data][:5]  # İlk 5 coin ile test
        
        logger.info(f"Test için {len(self.active_coins)} coin seçildi: {self.active_coins}")
        
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
        Tüm coinler için ML modellerini eğit
        """
        if not config.ML_ENABLED:
            logger.info("ML modeli devre dışı")
            return
        
        logger.info(f"{len(self.active_coins)} coin için model eğitimi başlatılıyor...")
        
        # Eğitimi sırayla yap (API limit'i için)
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
                symbol, config.ML_RETRAIN_INTERVAL_HOURS
            ):
                logger.info(f"{symbol} modeli güncellendi")
    
    async def get_ml_signal(self, symbol: str, current_data: pd.DataFrame) -> dict:
        """
        Belirli bir coin için ML sinyali al
        """
        if not config.ML_ENABLED:
            return {'score': 0, 'direction': 'NEUTRAL', 'confidence': 0}
        
        try:
            # ML tahminini al
            prediction = self.model_trainer.get_prediction(
                symbol, config.ML_PREDICTION_STEPS
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
                if model_confidence < config.ML_MIN_CONFIDENCE:
                    final_score = 0
                    direction = 'NEUTRAL'
                
                return {
                    'score': final_score,
                    'direction': direction,
                    'confidence': model_confidence,
                    'price_change_percent': price_change_percent,
                    'predicted_price': next_price,
                    'long_term_trend': long_term_trend,
                    'predictions': next_predictions,
                    'model_type': prediction.get('model_type', 'unknown'),
                    'best_model': prediction.get('best_model', 'unknown')
                }
            
        except Exception as e:
            logger.error(f"{symbol} ML sinyal hatası: {e}")
        
        return {'score': 0, 'direction': 'NEUTRAL', 'confidence': 0}
    
    def integrate_ml_with_existing_signals(self, symbol: str, 
                                         existing_score: float,
                                         ml_signal: dict) -> float:
        """
        ML sinyalini mevcut sinyal sistemiyle entegre et
        """
        if not config.ML_ENABLED or ml_signal['score'] == 0:
            return existing_score
        
        # ML ağırlığını uygula
        ml_contribution = ml_signal['score'] * config.ML_PREDICTION_WEIGHT
        
        # Sinyal yönleri uyumlu mu kontrol et
        if existing_score > 50 and ml_signal['direction'] == 'LONG':
            # Aynı yönde güçlendirme
            enhanced_score = existing_score + ml_contribution
        elif existing_score < 50 and ml_signal['direction'] == 'SHORT':
            # Aynı yönde güçlendirme  
            enhanced_score = existing_score - ml_contribution
        else:
            # Farklı yönlerde - daha konservatif yaklaşım
            enhanced_score = existing_score * (1 - config.ML_PREDICTION_WEIGHT * 0.5)
        
        # Sınırlara dahil et
        enhanced_score = max(0, min(100, enhanced_score))
        
        logger.debug(f"{symbol}: Orijinal skor {existing_score:.2f}, "
                    f"ML katkısı {ml_contribution:.2f}, "
                    f"Final skor {enhanced_score:.2f}")
        
        return enhanced_score
    
    async def get_ml_price_targets(self, symbol: str) -> dict:
        """
        ML tahminlerine göre fiyat hedeflerini hesapla
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
        
        # ML bazlı hedefler
        ml_targets = {
            'take_profit_price': max_predicted,
            'stop_loss_price': min_predicted,
            'confidence': prediction['confidence'],
            'prediction_horizon': len(predictions),
            'model_type': prediction.get('model_type', 'unknown')
        }
        
        return ml_targets
    
    async def send_ml_notification(self, symbol: str, prediction: dict):
        """
        ML tahmin bildirimini gönder
        """
        if not config.NOTIFY_ML_PREDICTIONS:
            return
        
        try:
            current_price = prediction['current_price']
            next_price = prediction['predictions'][0] if prediction['predictions'] else current_price
            confidence = prediction['confidence']
            model_type = prediction.get('model_type', 'ensemble')
            best_model = prediction.get('best_model', 'unknown')
            
            change_percent = ((next_price - current_price) / current_price) * 100
            
            message = f"""
🤖 ML Fiyat Tahmini
💰 {symbol}
📈 Mevcut: ${current_price:.4f}
🔮 Tahmin: ${next_price:.4f}
📊 Değişim: {change_percent:+.2f}%
🎯 Güven: {confidence:.1%}
🏆 Model: {model_type} ({best_model})
⏰ {datetime.now().strftime('%H:%M:%S')}
"""
            
            # Telegram'a gönder (mevcut telegram fonksiyonunu kullan)
            # await self.send_telegram_message(message)
            logger.info(f"ML bildirimi: {symbol} {change_percent:+.2f}% (Model: {best_model})")
            
        except Exception as e:
            logger.error(f"ML bildirim hatası: {e}")
    
    async def get_model_performance_summary(self) -> dict:
        """
        Tüm modellerin performans özeti
        """
        performance_summary = self.model_trainer.get_model_comparison()
        
        if not performance_summary:
            return {}
        
        # Ortalama performans
        avg_mape = sum(p['test_mape'] for p in performance_summary.values()) / len(performance_summary)
        best_performer = min(performance_summary.items(), key=lambda x: x[1]['test_mape'])
        worst_performer = max(performance_summary.items(), key=lambda x: x[1]['test_mape'])
        
        summary = {
            'total_models': len(performance_summary),
            'average_mape': avg_mape,
            'best_performer': {
                'symbol': best_performer[0],
                'mape': best_performer[1]['test_mape'],
                'model': best_performer[1]['best_model']
            },
            'worst_performer': {
                'symbol': worst_performer[0],
                'mape': worst_performer[1]['test_mape'],
                'model': worst_performer[1]['best_model']
            },
            'models_breakdown': performance_summary
        }
        
        return summary

# Ana bot entegrasyonu için örnek fonksiyon
async def enhanced_signal_calculation(symbol: str, market_data: pd.DataFrame, 
                                    ml_bot: MLTradingBot) -> float:
    """
    Mevcut sinyal hesaplamasına ML entegrasyonu örneği
    Bu fonksiyonu main.py'daki mevcut sinyal hesaplama fonksiyonunuza adapte edin
    """
    
    # 1. Mevcut teknik analiz sinyallerini hesapla (RSI, Bollinger, vb.)
    # existing_score = calculate_technical_signals(market_data)  # Mevcut fonksiyonunuz
    existing_score = 75.0  # Örnek değer
    
    # 2. ML sinyalini al
    ml_signal = await ml_bot.get_ml_signal(symbol, market_data)
    
    # 3. ML ile entegre et
    final_score = ml_bot.integrate_ml_with_existing_signals(
        symbol, existing_score, ml_signal
    )
    
    # 4. ML bildirimini gönder
    if ml_signal['score'] > 0:
        await ml_bot.send_ml_notification(symbol, ml_bot.predictions_cache.get(symbol, {}))
    
    return final_score

# Test fonksiyonu
async def test_ml_integration():
    """
    ML entegrasyonunu test et
    """
    bot = MLTradingBot()
    
    try:
        # Modelleri başlat
        await bot.initialize_models()
        
        # Test coin'i için tahmin al
        test_symbol = "BTCUSDT"
        
        # Son 200 saatlik veri al
        recent_data = bot.model_trainer.fetch_training_data(test_symbol, limit=200)
        
        if not recent_data.empty:
            # ML sinyali al
            ml_signal = await bot.get_ml_signal(test_symbol, recent_data)
            
            print(f"\n{test_symbol} ML Sinyali:")
            print(f"Skor: {ml_signal['score']:.2f}")
            print(f"Yön: {ml_signal['direction']}")
            print(f"Güven: {ml_signal['confidence']:.2%}")
            print(f"Model Tipi: {ml_signal.get('model_type', 'unknown')}")
            print(f"En İyi Model: {ml_signal.get('best_model', 'unknown')}")
            
            if 'predicted_price' in ml_signal:
                print(f"Tahmin edilen fiyat: ${ml_signal['predicted_price']:.2f}")
                print(f"Beklenen değişim: {ml_signal['price_change_percent']:+.2f}%")
        
        # Performans özeti
        print("\n" + "="*50)
        performance = await bot.get_model_performance_summary()
        if performance:
            print(f"Toplam model sayısı: {performance['total_models']}")
            print(f"Ortalama MAPE: {performance['average_mape']:.2f}%")
            print(f"En iyi performer: {performance['best_performer']['symbol']} "
                  f"({performance['best_performer']['mape']:.2f}%)")
        
    except Exception as e:
        logger.error(f"Test hatası: {e}")

if __name__ == "__main__":
    # Test çalıştır
    asyncio.run(test_ml_integration()) 