#!/usr/bin/env python3
"""
Quick ML Prediction Test
Hızlı ML Tahmin Testi

Kullanım: python quick_prediction.py BTCUSDT
"""

import sys
import os
import asyncio
import pandas as pd
from datetime import datetime
import logging

# Yolu ayarla
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

# ML modüllerini import et
from ml_models.model_trainer import ModelTrainer
from binance.client import Client

# Logging ayarla
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def quick_prediction(symbol: str):
    """Hızlı tahmin testi"""
    print(f"🔮 {symbol} için ML Tahmin Testi")
    print("=" * 50)
    
    try:
        # Model trainer oluştur
        trainer = ModelTrainer()
        
        # Eğitilmiş model var mı kontrol et
        if not trainer.is_model_trained(symbol):
            print(f"❌ {symbol} için eğitilmiş model bulunamadı!")
            print("💡 Önce modeli eğitin: python train_all_coins.py")
            return
        
        # Modeli yükle
        print(f"📦 {symbol} modeli yükleniyor...")
        predictor = trainer.load_trained_model(symbol)
        
        if predictor is None:
            print(f"❌ {symbol} modeli yüklenemedi!")
            return
        
        # Güncel veri al
        print(f"📊 {symbol} güncel verisi alınıyor...")
        df = await trainer.get_historical_data(symbol, days=30)
        
        if df is None:
            print(f"❌ {symbol} için veri alınamadı!")
            return
        
        # Tahmin yap
        print(f"🤖 ML tahmini yapılıyor...")
        result = predictor.predict(df)
        
        if not result['success']:
            print(f"❌ Tahmin hatası: {result['error']}")
            return
        
        # Sonuçları göster
        current_price = result['current_price']
        prediction = result['prediction']
        change_pct = result['price_change_pct']
        confidence = result['confidence']
        trend = result['trend']
        
        print(f"\n📈 SONUÇLAR:")
        print(f"💰 Mevcut Fiyat: ${current_price:.6f}")
        print(f"🔮 Tahmin Fiyat: ${prediction:.6f}")
        print(f"📊 Değişim: {change_pct:+.2f}%")
        print(f"🎯 Güven Skoru: {confidence:.1%}")
        print(f"📈 Trend: {trend}")
        
        # Renkli çıktı
        if change_pct > 0:
            print(f"🟢 Yükselme bekleniyor!")
        else:
            print(f"🔴 Düşüş bekleniyor!")
        
        # Güven seviyesi
        if confidence > 0.8:
            print(f"✅ Yüksek güven seviyesi")
        elif confidence > 0.6:
            print(f"⚠️  Orta güven seviyesi")
        else:
            print(f"🚨 Düşük güven seviyesi")
        
        # Individual model predictions
        if 'individual_predictions' in result:
            print(f"\n🔍 MODEL DETAYLARI:")
            for model_name, pred in result['individual_predictions'].items():
                model_change = ((pred - current_price) / current_price) * 100
                print(f"   {model_name}: ${pred:.6f} ({model_change:+.2f}%)")
        
        print(f"\n⏰ Tahmin Zamanı: {result['timestamp']}")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

def main():
    """Ana fonksiyon"""
    if len(sys.argv) != 2:
        print("Kullanım: python quick_prediction.py SEMBOL")
        print("Örnek: python quick_prediction.py BTCUSDT")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    if not symbol.endswith('USDT'):
        symbol += 'USDT'
    
    asyncio.run(quick_prediction(symbol))

if __name__ == "__main__":
    main() 