#!/usr/bin/env python3
"""
İlk 10 Coin için Hızlı Test
Tüm coinlerden önce 10 coin ile test yapalım
"""

import asyncio
import json
import sys
import os

# Parent dizini path'e ekle (config.py için)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.client import Client
from ml_models import ModelTrainer
import config

async def train_first_10():
    """İlk 10 coin için eğitim"""
    
    # Coin listesini yükle
    with open(config.COIN_LIST_FILE, 'r') as f:
        coin_data = json.load(f)
    
    # İlk 10 coini al
    coins = [coin.replace('/', '') for coin in coin_data['coins'][:10]]
    
    print(f"🎯 İlk 10 coin için eğitim: {coins}")
    print("⏱️  Tahmini süre: 15-20 dakika")
    
    # Trainer başlat
    client = Client(config.API_KEY, config.API_SECRET)
    trainer = ModelTrainer(client)
    
    # Eğitimi başlat
    results = trainer.train_all_models(coins)
    
    # Sonuçları göster
    print("\n" + "="*50)
    print("📊 İLK 10 COİN EĞİTİM SONUÇLARI:")
    print("="*50)
    
    successful = sum(results.values())
    total = len(results)
    
    print(f"✅ Başarılı: {successful}/{total}")
    print(f"📈 Başarı oranı: {successful/total*100:.1f}%")
    
    # Performans detayları
    for symbol in coins:
        if symbol in trainer.models:
            performance = trainer.get_model_performance(symbol)
            test_mape = performance['training_history'].get('test_mape', 0)
            best_model = performance['training_history'].get('best_model', 'unknown')
            status = "✅" if results.get(symbol, False) else "❌"
            print(f"{status} {symbol:10} | MAPE: {test_mape:5.2f}% | Model: {best_model}")
    
    print("\n🎉 Test tamamlandı! Şimdi tüm coinleri eğitmek için:")
    print("python train_all_coins.py")

if __name__ == "__main__":
    asyncio.run(train_first_10()) 