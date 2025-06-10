#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Whale Position Tracker Demo Script
Bu script, whale position tracker'ın temel özelliklerini test etmek için kullanılır.
"""

import json
import time
from datetime import datetime
from whale_position_tracker import WhalePositionTracker

def main():
    print("🐋 Whale Position Tracker Demo Başlatılıyor...")
    print("=" * 50)
    
    try:
        # Tracker'ı başlat
        tracker = WhalePositionTracker()
        print("✅ Tracker başarıyla oluşturuldu")
        
        # Test coinleri
        test_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        
        print(f"\n📊 Test Coinleri: {', '.join(test_symbols)}")
        print("-" * 30)
        
        for symbol in test_symbols:
            print(f"\n🔍 {symbol} analiz ediliyor...")
            
            try:
                # Büyük işlemleri analiz et
                large_trades = tracker.analyze_large_trades(symbol, limit=100)
                print(f"   📈 {len(large_trades)} büyük işlem bulundu")
                
                if large_trades:
                    # En büyük işlemi göster
                    largest = max(large_trades, key=lambda x: x['value'])
                    print(f"   💎 En büyük işlem: ${largest['value']:,.0f} ({largest['whale_type']})")
                    print(f"   🕒 Zaman: {largest['datetime'].strftime('%H:%M:%S')}")
                    print(f"   📍 Pozisyon: {largest['position_side']}")
                
                # Pozisyon analizi yap
                positions = tracker.detect_whale_positions(symbol)
                if positions:
                    for pos in positions:
                        print(f"   🎯 Dominant Pozisyon: {pos['dominant_side']}")
                        print(f"   📊 Güven: {pos['confidence']:.1%}")
                        print(f"   🔥 Aktivite: {pos['whale_activity_level']}")
                        print(f"   💰 Toplam Hacim: ${pos['total_volume']:,.0f}")
                else:
                    print(f"   ℹ️  Önemli whale aktivitesi tespit edilmedi")
                
                # API rate limit için kısa bekleme
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Hata: {e}")
                continue
        
        print("\n" + "=" * 50)
        print("📈 Genel İstatistikler")
        print("-" * 20)
        
        # Whale summary al
        summary = tracker.get_whale_summary()
        print(f"📊 Toplam İzlenen Coin: {summary['total_monitored_coins']}")
        print(f"🪙 Aktif Coin: {summary['active_coins']}")
        print(f"🎭 Genel Sentiment: {summary['overall_sentiment']}")
        
        if summary['top_whale_coins']:
            print("\n🏆 Top Whale Aktiviteleri:")
            for i, coin in enumerate(summary['top_whale_coins'][:3], 1):
                side_emoji = "🟢" if coin['dominant_side'] == 'LONG' else "🔴" if coin['dominant_side'] == 'SHORT' else "🟡"
                print(f"   {i}. {side_emoji} {coin['symbol']} - ${coin['total_volume']:,.0f}")
        
        print("\n✅ Demo tamamlandı!")
        print("\n💡 Sürekli takip için ana script'i çalıştırın:")
        print("   python whale_position_tracker.py")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo durduruldu")
    except Exception as e:
        print(f"\n❌ Demo hatası: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. API anahtarlarınızı config.py'da kontrol edin")
        print("   2. Internet bağlantınızı kontrol edin")
        print("   3. requirements.txt bağımlılıklarını yükleyin")

def test_configuration():
    """Konfigürasyonu test eder"""
    print("🔧 Konfigürasyon Test Ediliyor...")
    
    try:
        from config import API_KEY, API_SECRET, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        
        # API anahtarları kontrol
        print(f"🔑 API Key: ...{API_KEY[-4:] if API_KEY else 'YOK'}")
        print(f"🗝️ API Secret: ...{API_SECRET[-4:] if API_SECRET else 'YOK'}")
        
        if API_KEY and len(API_KEY) > 10:
            print("✅ Binance API anahtarı bulundu")
        else:
            print("⚠️  Binance API anahtarı eksik - config.py'da düzenleyin")
        
        if API_SECRET and len(API_SECRET) > 10:
            print("✅ Binance API secret bulundu")
        else:
            print("⚠️  Binance API secret eksik - config.py'da düzenleyin")
        
        # Telegram kontrol
        if TELEGRAM_BOT_TOKEN and len(TELEGRAM_BOT_TOKEN) > 10:
            print("✅ Telegram bot token bulundu")
        else:
            print("⚠️  Telegram bot token eksik - bildirimler çalışmayacak")
        
        if TELEGRAM_CHAT_ID and len(str(TELEGRAM_CHAT_ID)) > 5:
            print("✅ Telegram chat ID bulundu")
        else:
            print("⚠️  Telegram chat ID eksik - bildirimler çalışmayacak")
            
    except ImportError:
        print("❌ config.py dosyası bulunamadı")
        return False
    
    print("✅ Konfigürasyon kontrolü tamamlandı\n")
    return True

if __name__ == "__main__":
    print("🐋 Whale Position Tracker Demo")
    print("Bu demo, whale tracker'ın temel özelliklerini test eder.\n")
    
    # Önce konfigürasyonu test et
    if test_configuration():
        # Ana demo'yu çalıştır
        main()
    else:
        print("❌ Lütfen önce konfigürasyonu düzenleyin") 