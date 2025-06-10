"""
Whale Tracker Demo
Test ve demo amaçlı whale tracker kullanımı
"""

import sys
import os
import time
import logging
from datetime import datetime

# Sys path'i ayarla - whale_tracker modülünü bul
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import whale tracker bileşenleri
from whale_tracker.whale_tracker import WhaleTracker

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def demo_whale_tracker():
    """
    Whale tracker'ı demo et
    """
    print("🐋 WHALE TRACKER DEMO BAŞLATIYOR...")
    print("=" * 60)
    
    # Whale tracker'ı başlat
    tracker = WhaleTracker()
    
    try:
        # 1. Manuel scan testi
        print("\n📊 MANUEL WHALE SCAN TESİT EDİLİYOR...")
        scan_result = tracker.manual_scan()
        print(f"Scan sonucu: {scan_result.get('whale_stats', {}).get('total_24h', 0)} whale tespit edildi")
        
        # 2. Aktif sinyalleri göster
        print("\n📈 AKTİF SİNYALLER:")
        active_signals = tracker.get_active_signals()
        if active_signals:
            for signal in active_signals[:5]:  # İlk 5 sinyal
                print(f"   • {signal['symbol']}: {signal['signal_type']} ({signal['confidence']:.1%})")
        else:
            print("   Henüz aktif sinyal yok")
        
        # 3. Son whale hareketleri
        print("\n🐋 SON WHALE HAREKETLERİ:")
        recent_whales = tracker.get_recent_whales(hours_back=24, limit=5)
        if recent_whales:
            for whale in recent_whales:
                symbol = whale.get('symbol', 'UNKNOWN')
                amount_usd = whale.get('amount_usd', 0)
                from_addr = whale.get('from', 'unknown')[:15]
                to_addr = whale.get('to', 'unknown')[:15]
                print(f"   • {symbol}: ${amount_usd:,.0f} ({from_addr}→{to_addr})")
        else:
            print("   Son 24 saatte whale hareketi tespit edilmedi")
        
        # 4. Whale summary
        print("\n📋 WHALE TRACKER ÖZETİ:")
        summary = tracker.get_whale_summary()
        print(f"   Status: {summary.get('status', 'UNKNOWN')}")
        print(f"   24h Whale Count: {summary.get('whale_stats', {}).get('total_24h', 0)}")
        print(f"   Aktif Sinyal: {summary.get('active_signals_count', 0)}")
        
        # 5. Analytics test
        print("\n🔍 WHALE ANALİTİKLERİ:")
        analytics = tracker.get_whale_analytics(hours_back=24)
        if not analytics.get('no_data'):
            total_volume = analytics.get('total_volume_usd', 0)
            total_whales = analytics.get('total_whales', 0)
            avg_volume = analytics.get('avg_volume_usd', 0)
            
            print(f"   Toplam Volume: ${total_volume:,.0f}")
            print(f"   Toplam Whale: {total_whales}")
            print(f"   Ortalama Volume: ${avg_volume:,.0f}")
            
            # Sentiment
            sentiment = analytics.get('sentiment', {})
            if sentiment:
                overall_sentiment = sentiment.get('overall_sentiment', 'NEUTRAL')
                confidence = sentiment.get('confidence', 0)
                print(f"   Whale Sentiment: {overall_sentiment} ({confidence:.1%})")
        else:
            print("   Analiz için yeterli veri yok")
        
        # 6. Monitoring test (kısa süre)
        print("\n⏰ WHALE MONİTORİNG TEST EDİLİYOR (30 saniye)...")
        tracker.start_monitoring()
        
        print("   Monitoring başlatıldı. 30 saniye bekleniyor...")
        time.sleep(30)
        
        tracker.stop_monitoring()
        print("   Monitoring durduruldu.")
        
        # Final summary
        print("\n📊 FİNAL SUMMARY:")
        final_summary = tracker.get_whale_summary()
        metrics = final_summary.get('performance_metrics', {})
        
        print(f"   Total API Calls: {metrics.get('api_calls_made', 0)}")
        print(f"   Whales Detected: {metrics.get('total_whales_detected', 0)}")
        print(f"   Signals Generated: {metrics.get('signals_generated', 0)}")
        print(f"   Notifications Sent: {metrics.get('notifications_sent', 0)}")
        
        print("\n✅ WHALE TRACKER DEMO TAMAMLANDI!")
        
    except Exception as e:
        print(f"\n❌ Demo sırasında hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if tracker.is_running:
            tracker.stop_monitoring()

def test_whale_signals():
    """
    Whale signal generation test
    """
    print("\n🧪 WHALE SİNYAL GENERATİON TEST")
    print("=" * 50)
    
    tracker = WhaleTracker()
    
    # Mock whale data
    mock_whale_data = {
        'symbol': 'BTC',
        'amount': 250.5,
        'amount_usd': 27555000,
        'timestamp': int(time.time() - 3600),
        'from': 'unknown',
        'to': 'binance',
        'hash': 'test_hash_123'
    }
    
    # Analiz et
    analysis = tracker.analyzer.analyze_whale_movement(mock_whale_data)
    print(f"Whale Analysis: {analysis.get('signal_type')} ({analysis.get('confidence', 0):.1%})")
    
    # Signal üret
    if analysis.get('confidence', 0) > 0.5:
        signal = tracker.signal_generator._create_signal(
            symbol=mock_whale_data['symbol'],
            signal_type=analysis['signal_type'],
            confidence=analysis['confidence'],
            source='test'
        )
        
        if signal:
            print(f"Generated Signal: {signal['id']}")
            print(f"   Type: {signal['signal_type']}")
            print(f"   Strength: {signal['strength']}")
            print(f"   Confidence: {signal['confidence']:.1%}")
    
    # Notification test
    tracker.notifier.notify_whale_movement(mock_whale_data, analysis)
    
    print("✅ Signal test tamamlandı")

def test_whale_patterns():
    """
    Whale pattern detection test
    """
    print("\n🔍 WHALE PATTERN TESPİT TEST")
    print("=" * 50)
    
    tracker = WhaleTracker()
    
    # Mock whale history (accumulation pattern simülasyonu)
    mock_whales = []
    
    # 5 büyük withdrawal (exchange'den çıkış)
    for i in range(5):
        whale = {
            'symbol': 'BTC',
            'amount': 100 + (i * 20),
            'amount_usd': (100 + (i * 20)) * 110000,
            'timestamp': int(time.time() - (i * 3600)),  # Her saat bir
            'from': 'binance',
            'to': 'unknown',
            'hash': f'test_withdrawal_{i}'
        }
        mock_whales.append(whale)
    
    # Pattern analizi
    patterns = tracker.analyzer.detect_whale_patterns(mock_whales, hours_lookback=24)
    
    print(f"Pattern Confidence: {patterns.get('pattern_confidence', 0):.1%}")
    
    pattern_types = [
        ('accumulation_pattern', 'Accumulation'),
        ('distribution_pattern', 'Distribution'),
        ('exchange_exodus', 'Exchange Exodus'),
        ('coordinated_selling', 'Coordinated Selling'),
        ('whale_rotation', 'Whale Rotation')
    ]
    
    for pattern_key, pattern_name in pattern_types:
        if patterns.get(pattern_key, False):
            print(f"   ✅ {pattern_name} detected!")
    
    if patterns.get('pattern_confidence', 0) > 0.6:
        # Pattern signals üret
        pattern_signals = tracker.signal_generator.generate_pattern_signals(patterns)
        print(f"   Generated {len(pattern_signals)} pattern signals")
        
        # Pattern notification
        tracker.notifier.notify_pattern_detected(patterns)
    
    print("✅ Pattern test tamamlandı")

def benchmark_whale_tracker():
    """
    Whale tracker performance test
    """
    print("\n⚡ WHALE TRACKER PERFORMANCE TEST")
    print("=" * 50)
    
    tracker = WhaleTracker()
    
    start_time = time.time()
    
    # 100 mock whale analizi
    mock_whales = []
    for i in range(100):
        whale = {
            'symbol': f'COIN{i%10}',
            'amount': 100 + i,
            'amount_usd': (100 + i) * 1000,
            'timestamp': int(time.time() - (i * 60)),
            'from': 'unknown' if i % 2 == 0 else 'binance',
            'to': 'binance' if i % 2 == 0 else 'unknown',
            'hash': f'test_hash_{i}'
        }
        mock_whales.append(whale)
    
    # Bulk analiz
    analysis_start = time.time()
    analysis = tracker.analyzer.analyze_multiple_whales(mock_whales)
    analysis_time = time.time() - analysis_start
    
    # Signal generation
    signal_start = time.time()
    signals = tracker.signal_generator.generate_signals(analysis)
    signal_time = time.time() - signal_start
    
    total_time = time.time() - start_time
    
    print(f"   100 Whale Analysis: {analysis_time:.3f}s")
    print(f"   Signal Generation: {signal_time:.3f}s")
    print(f"   Total Time: {total_time:.3f}s")
    print(f"   Generated Signals: {len(signals)}")
    print(f"   Performance: {100/total_time:.1f} whales/second")
    
    print("✅ Performance test tamamlandı")

def interactive_whale_tracker():
    """
    İnteraktif whale tracker kontrolü
    """
    print("\n🎮 İNTERAKTİF WHALE TRACKER")
    print("=" * 50)
    
    tracker = WhaleTracker()
    
    while True:
        print("\n📋 KOMUTLAR:")
        print("1. Manual Scan")
        print("2. Active Signals")
        print("3. Recent Whales")
        print("4. Start Monitoring")
        print("5. Stop Monitoring")
        print("6. Analytics")
        print("7. Export Data")
        print("8. Test Telegram")
        print("9. Telegram Bot Info")
        print("0. Çıkış")
        
        try:
            choice = input("\nKomut seçin (0-9): ").strip()
            
            if choice == '0':
                print("Çıkış yapılıyor...")
                break
                
            elif choice == '1':
                print("📊 Manuel scan başlatılıyor...")
                result = tracker.manual_scan()
                print(f"Sonuç: {result.get('whale_stats', {}).get('total_24h', 0)} whale")
                
            elif choice == '2':
                signals = tracker.get_active_signals()
                print(f"📈 Aktif sinyal sayısı: {len(signals)}")
                for signal in signals[:5]:
                    print(f"   {signal['symbol']}: {signal['signal_type']}")
                    
            elif choice == '3':
                whales = tracker.get_recent_whales(hours_back=24, limit=10)
                print(f"🐋 Son 24h whale sayısı: {len(whales)}")
                for whale in whales[:5]:
                    print(f"   {whale.get('symbol')}: ${whale.get('amount_usd', 0):,.0f}")
                    
            elif choice == '4':
                print("▶️ Monitoring başlatılıyor...")
                tracker.start_monitoring()
                print("Monitoring aktif!")
                
            elif choice == '5':
                print("⏹️ Monitoring durduruluyor...")
                tracker.stop_monitoring()
                print("Monitoring durduruldu!")
                
            elif choice == '6':
                print("🔍 Analytics hesaplanıyor...")
                analytics = tracker.get_whale_analytics(hours_back=24)
                if not analytics.get('no_data'):
                    print(f"   Volume: ${analytics.get('total_volume_usd', 0):,.0f}")
                    print(f"   Whale Count: {analytics.get('total_whales', 0)}")
                else:
                    print("   Yeterli veri yok")
                    
            elif choice == '7':
                filename = f"whale_export_{int(time.time())}.json"
                tracker.export_data(filename)
                print(f"📁 Veriler {filename} dosyasına export edildi")
                
            elif choice == '8':
                print("🤖 Telegram bağlantısı test ediliyor...")
                test_telegram_integration(tracker)
                
            elif choice == '9':
                print("🔍 Telegram bot bilgileri alınıyor...")
                get_telegram_bot_status(tracker)
                
            else:
                print("❌ Geçersiz komut")
                
        except KeyboardInterrupt:
            print("\n\nÇıkış yapılıyor...")
            break
        except Exception as e:
            print(f"❌ Hata: {e}")
    
    # Cleanup
    if tracker.is_running:
        tracker.stop_monitoring()

def test_telegram_integration(tracker):
    """
    Telegram entegrasyonunu test et
    """
    try:
        print("🤖 TELEGRAM ENTEGRASYON TEST")
        print("-" * 40)
        
        notifier = tracker.notifier
        
        # 1. Konfigürasyon kontrolü
        print("⚙️ Konfigürasyon kontrol ediliyor...")
        print(f"   Telegram Enabled: {notifier.telegram_enabled}")
        print(f"   Bot Token: {notifier.telegram_token[:10] + '...' if notifier.telegram_token else 'YOK'}")
        print(f"   Chat ID: {notifier.telegram_chat_id}")
        
        if not notifier.telegram_enabled:
            print("❌ Telegram devre dışı bırakılmış")
            return
        
        if not notifier.telegram_token or notifier.telegram_token == "your_telegram_bot_token":
            print("❌ Bot token konfigüre edilmemiş")
            print("💡 whale_config.py'da TELEGRAM_BOT_TOKEN'ı ayarlayın")
            return
        
        if not notifier.telegram_chat_id or notifier.telegram_chat_id == "your_chat_id":
            print("❌ Chat ID konfigüre edilmemiş")
            print("💡 whale_config.py'da TELEGRAM_CHAT_ID'yi ayarlayın")
            return
        
        # 2. Bot bilgilerini al
        print("\n🤖 Bot bilgileri alınıyor...")
        bot_info = notifier.get_telegram_bot_info()
        
        if bot_info.get('status') == 'OK':
            bot_data = bot_info.get('bot_info', {})
            print(f"   ✅ Bot Name: {bot_data.get('first_name', 'N/A')}")
            print(f"   ✅ Bot Username: @{bot_data.get('username', 'N/A')}")
            print(f"   ✅ Bot ID: {bot_data.get('id', 'N/A')}")
        else:
            print(f"   ❌ Bot bilgisi alınamadı: {bot_info.get('error', 'Unknown error')}")
            return
        
        # 3. Test mesajı gönder
        print("\n📤 Test mesajı gönderiliyor...")
        test_result = notifier.test_telegram_connection()
        
        if test_result:
            print("   ✅ Test mesajı başarıyla gönderildi!")
            print("   📱 Telegram'ı kontrol edin")
        else:
            print("   ❌ Test mesajı gönderilemedi")
            return
        
        # 4. Örnek whale bildirimi
        print("\n🐋 Örnek whale bildirimi gönderiliyor...")
        
        mock_whale = {
            'symbol': 'BTC',
            'amount': 150.25,
            'amount_usd': 16527500,
            'timestamp': int(time.time()),
            'from': 'unknown',
            'to': 'binance',
            'hash': 'test_whale_telegram'
        }
        
        mock_analysis = {
            'signal_type': 'BEARISH',
            'confidence': 0.82,
            'strength': 'MAJOR',
            'reasoning': ['Büyük exchange deposit', 'Satış baskısı riski'],
            'recommended_action': {'primary': 'CONSIDER_SELL'}
        }
        
        notifier.notify_whale_movement(mock_whale, mock_analysis)
        print("   ✅ Örnek whale bildirimi gönderildi!")
        
        # 5. Örnek sinyal bildirimi
        print("\n📈 Örnek sinyal bildirimi gönderiliyor...")
        
        mock_signals = [
            {
                'symbol': 'BTC',
                'signal_type': 'BEARISH',
                'confidence': 0.82,
                'strength': 'STRONG'
            },
            {
                'symbol': 'ETH',
                'signal_type': 'BULLISH', 
                'confidence': 0.71,
                'strength': 'MODERATE'
            }
        ]
        
        notifier.notify_signal_generated(mock_signals)
        print("   ✅ Örnek sinyal bildirimi gönderildi!")
        
        print("\n✅ TELEGRAM ENTEGRASYON TEST TAMAMLANDI!")
        print("📱 Telegram uygulamanızı kontrol edin")
        
    except Exception as e:
        print(f"❌ Telegram test hatası: {e}")
        import traceback
        traceback.print_exc()

def get_telegram_bot_status(tracker):
    """
    Telegram bot durumunu göster
    """
    try:
        notifier = tracker.notifier
        
        print("🤖 TELEGRAM BOT DURUM")
        print("-" * 30)
        
        # Konfigürasyon durumu
        print("⚙️ Konfigürasyon:")
        print(f"   Enabled: {notifier.telegram_enabled}")
        print(f"   Token Set: {'✅' if notifier.telegram_token and notifier.telegram_token != 'your_telegram_bot_token' else '❌'}")
        print(f"   Chat ID Set: {'✅' if notifier.telegram_chat_id and notifier.telegram_chat_id != 'your_chat_id' else '❌'}")
        
        if not (notifier.telegram_enabled and notifier.telegram_token and notifier.telegram_chat_id):
            print("\n❌ Telegram tam olarak konfigüre edilmemiş")
            print("💡 TELEGRAM_SETUP.md dosyasını inceleyin")
            return
        
        # Bot bilgileri
        print("\n🤖 Bot Bilgileri:")
        bot_info = notifier.get_telegram_bot_info()
        
        if bot_info.get('status') == 'OK':
            bot_data = bot_info.get('bot_info', {})
            print(f"   Name: {bot_data.get('first_name', 'N/A')}")
            print(f"   Username: @{bot_data.get('username', 'N/A')}")
            print(f"   ID: {bot_data.get('id', 'N/A')}")
            print(f"   Can Join Groups: {bot_data.get('can_join_groups', False)}")
            print(f"   Can Read Messages: {bot_data.get('can_read_all_group_messages', False)}")
        else:
            print(f"   ❌ Bot bilgisi alınamadı: {bot_info.get('error', 'Unknown')}")
        
        # Bildirim ayarları
        print("\n📱 Bildirim Ayarları:")
        try:
            from . import whale_config as config
            print(f"   Whale Movements: {getattr(config, 'TELEGRAM_SEND_WHALE_MOVEMENTS', False)}")
            print(f"   Signals: {getattr(config, 'TELEGRAM_SEND_SIGNALS', False)}")
            print(f"   Patterns: {getattr(config, 'TELEGRAM_SEND_PATTERNS', False)}")
            print(f"   Alerts: {getattr(config, 'TELEGRAM_SEND_ALERTS', False)}")
            print(f"   Only Strong: {getattr(config, 'TELEGRAM_SEND_ONLY_STRONG', False)}")
            print(f"   Parse Mode: {getattr(config, 'TELEGRAM_PARSE_MODE', 'Markdown')}")
        except:
            print("   Config bilgisi alınamadı")
        
        print("\n✅ Bot durum kontrolü tamamlandı")
        
    except Exception as e:
        print(f"❌ Bot durum kontrol hatası: {e}")

if __name__ == "__main__":
    print("🐋 WHALE TRACKER TEST SÜİTİ")
    print("=" * 60)
    
    try:
        # Ana demo
        demo_whale_tracker()
        
        # Test suites
        test_whale_signals()
        test_whale_patterns()
        benchmark_whale_tracker()
        
        # İnteraktif mod
        choice = input("\nİnteraktif modu başlatmak ister misiniz? (y/n): ").strip().lower()
        if choice == 'y':
            interactive_whale_tracker()
        
    except KeyboardInterrupt:
        print("\n\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\nGenel hata: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 WHALE TRACKER TEST TAMAMLANDI!") 