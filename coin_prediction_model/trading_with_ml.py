#!/usr/bin/env python3
"""
Trading with ML Integration
ML Entegrasyonlu Trading Örneği

Bu dosya mevcut trading botuna ML tahminlerinin nasıl entegre edileceğini gösterir.
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# Yolu ayarla
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

# ML modüllerini import et
from ml_models.model_trainer import ModelTrainer

# Logging ayarla
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLTradingSignals:
    """ML tahminleri ile trading sinyalleri"""
    
    def __init__(self):
        self.trainer = ModelTrainer()
        self.loaded_models = {}
        logger.info("ML Trading Signals başlatıldı")
    
    async def load_model_for_symbol(self, symbol: str):
        """Coin için modeli yükle"""
        if symbol not in self.loaded_models:
            if self.trainer.is_model_trained(symbol):
                predictor = self.trainer.load_trained_model(symbol)
                if predictor:
                    self.loaded_models[symbol] = predictor
                    logger.info(f"✅ {symbol} modeli yüklendi")
                    return True
                else:
                    logger.warning(f"❌ {symbol} modeli yüklenemedi")
                    return False
            else:
                logger.warning(f"❌ {symbol} için eğitilmiş model yok")
                return False
        return True
    
    async def get_ml_signal(self, symbol: str, df=None) -> dict:
        """ML sinyali al"""
        try:
            # Model yükle
            if not await self.load_model_for_symbol(symbol):
                return {'success': False, 'error': 'Model yüklenemedi'}
            
            # Veri al (eğer verilmemişse)
            if df is None:
                df = await self.trainer.get_historical_data(symbol, days=30)
                if df is None:
                    return {'success': False, 'error': 'Veri alınamadı'}
            
            # Tahmin yap
            predictor = self.loaded_models[symbol]
            result = predictor.predict(df)
            
            if not result['success']:
                return result
            
            # Trading sinyali oluştur
            signal = self._convert_to_trading_signal(result)
            signal['symbol'] = symbol
            signal['timestamp'] = datetime.now().isoformat()
            
            return signal
            
        except Exception as e:
            logger.error(f"ML sinyal hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    def _convert_to_trading_signal(self, ml_result: dict) -> dict:
        """ML sonucunu trading sinyaline çevir"""
        try:
            price_change_pct = ml_result['price_change_pct']
            confidence = ml_result['confidence']
            
            # Sinyal gücü hesapla
            signal_strength = abs(price_change_pct) * confidence
            
            # Yön belirle
            direction = 'LONG' if price_change_pct > 0 else 'SHORT'
            
            # Sinyal seviyesi
            if signal_strength > 3.0 and confidence > 0.8:
                signal_level = 'STRONG'
            elif signal_strength > 1.5 and confidence > 0.6:
                signal_level = 'MEDIUM'
            elif signal_strength > 0.5 and confidence > 0.5:
                signal_level = 'WEAK'
            else:
                signal_level = 'NONE'
            
            # Trading önerisi
            should_trade = (
                signal_level in ['STRONG', 'MEDIUM'] and 
                confidence >= config.ML_MIN_CONFIDENCE and
                abs(price_change_pct) >= config.ML_SIGNAL_THRESHOLD
            )
            
            return {
                'success': True,
                'direction': direction,
                'signal_level': signal_level,
                'signal_strength': signal_strength,
                'price_change_pct': price_change_pct,
                'confidence': confidence,
                'should_trade': should_trade,
                'current_price': ml_result['current_price'],
                'predicted_price': ml_result['prediction'],
                'trend': ml_result['trend']
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Sinyal dönüşüm hatası: {e}'}
    
    async def get_multiple_signals(self, symbols: list) -> dict:
        """Çoklu coin için sinyaller"""
        results = {}
        
        for symbol in symbols:
            logger.info(f"🔍 {symbol} sinyali alınıyor...")
            signal = await self.get_ml_signal(symbol)
            results[symbol] = signal
            
            if signal['success'] and signal['should_trade']:
                direction = signal['direction']
                level = signal['signal_level']
                confidence = signal['confidence']
                logger.info(f"🎯 {symbol}: {direction} {level} sinyal (Güven: {confidence:.1%})")
        
        return results

async def demo_ml_trading():
    """ML trading demo"""
    print("🤖 ML TRADING SİNYALLERİ DEMO")
    print("=" * 50)
    
    # ML signals oluştur
    ml_signals = MLTradingSignals()
    
    # Test coinleri
    test_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
    
    # Sinyalleri al
    results = await ml_signals.get_multiple_signals(test_coins)
    
    # Sonuçları göster
    print("\n📊 ML SİNYAL SONUÇLARI:")
    print("-" * 70)
    
    for symbol, result in results.items():
        if result['success']:
            direction = result['direction']
            level = result['signal_level']
            confidence = result['confidence']
            change_pct = result['price_change_pct']
            should_trade = result['should_trade']
            
            # Emoji seç
            if should_trade:
                if level == 'STRONG':
                    emoji = "🟢🚀"
                elif level == 'MEDIUM':
                    emoji = "🟡⚡"
                else:
                    emoji = "🟠📈"
            else:
                emoji = "⚪⏸️"
            
            print(f"{emoji} {symbol}: {direction} {level}")
            print(f"    💰 Fiyat Değişimi: {change_pct:+.2f}%")
            print(f"    🎯 Güven: {confidence:.1%}")
            print(f"    📊 Trade Önerisi: {'EVET' if should_trade else 'HAYIR'}")
            print()
        else:
            print(f"❌ {symbol}: {result['error']}")
            print()
    
    # Trading önerileri özeti
    tradeable_signals = [r for r in results.values() if r.get('success') and r.get('should_trade')]
    
    if tradeable_signals:
        print(f"🎯 TRADING ÖNERİLERİ ({len(tradeable_signals)} adet):")
        print("-" * 40)
        
        for symbol, result in results.items():
            if result.get('success') and result.get('should_trade'):
                direction = result['direction']
                level = result['signal_level']
                confidence = result['confidence']
                
                print(f"   💡 {symbol}: {direction} pozisyonu aç ({level} sinyal)")
                print(f"      Güven: {confidence:.1%}")
                
                # Position sizing önerisi
                if level == 'STRONG':
                    size_multiplier = config.POSITION_SIZE_MAPPING['STRONG']
                elif level == 'MEDIUM':
                    size_multiplier = config.POSITION_SIZE_MAPPING['MEDIUM']
                else:
                    size_multiplier = config.POSITION_SIZE_MAPPING['WEAK']
                
                suggested_amount = config.TRADE_AMOUNT * size_multiplier
                print(f"      Önerilen Miktar: ${suggested_amount:.1f}")
                print()
    else:
        print("⚪ Şu anda güçlü ML sinyali bulunmuyor.")
    
    print("\n💡 Bu sonuçlar demo amaçlıdır. Gerçek trading yapmadan önce:")
    print("   ✅ Risk yönetimini kontrol edin")
    print("   ✅ Diğer analiz araçlarıyla doğrulayın")
    print("   ✅ Pozisyon boyutlarını ayarlayın")

def main():
    """Ana fonksiyon"""
    asyncio.run(demo_ml_trading())

if __name__ == "__main__":
    main() 