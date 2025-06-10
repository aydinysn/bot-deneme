# 🐋 Whale Tracker

Kripto piyasasındaki büyük cüzdan hareketlerini takip eden ve trading sinyalleri üreten gelişmiş sistem.

## 🎯 Ne İşe Yarar?

Whale Tracker, büyük kripto transferlerini tespit ederek:
- **Erken Uyarı**: Büyük fiyat değişimlerinden önce sinyal verir
- **Trading Sinyalleri**: BULLISH/BEARISH sinyaller üretir  
- **Pattern Tespiti**: Accumulation/Distribution patternlerini bulur
- **Risk Yönetimi**: Exchange akışlarını monitor eder
- **Otomatik Bildirim**: Anlık uyarılar gönderir

## 🚀 Özellikler

### 🔍 Whale Detection
- **Binance**: En büyük exchange akışları
- **Bitcoin**: 100+ BTC transferleri
- **Ethereum**: 1000+ ETH transferleri  
- **Diğer Coinler**: $1M+ USD değerindeki transferler

### 📊 Analiz Yetenekleri
- **Signal Types**: BULLISH, BEARISH, NEUTRAL
- **Confidence Scoring**: %60+ güvenilir sinyaller
- **Pattern Recognition**: 5 farklı whale pattern
- **Sentiment Analysis**: Piyasa duygu analizi

### 🎯 Trading Signals
- **Strength Levels**: MINOR → EXTREME
- **Auto-Expiry**: 4 saatte geçersiz
- **Rate Limiting**: Aynı coin için 5dk ara
- **Risk Assessment**: LOW/MEDIUM/HIGH

### 📱 Notifications
- **Console**: Anlık konsol bildirimleri
- **Email**: SMTP entegrasyonu (opsiyonel)
- **Discord**: Webhook desteği (opsiyonel)
- **Telegram**: Bot API (opsiyonel)

## 📁 Dosya Yapısı

```
whale_tracker/
├── __init__.py              # Modül init
├── whale_config.py          # Tüm ayarlar
├── whale_api.py             # API entegrasyonları
├── whale_analyzer.py        # Analiz motor
├── whale_signals.py         # Sinyal üreticisi
├── whale_notifications.py   # Bildirim sistemi
├── whale_tracker.py         # Ana kontrol sınıfı
├── whale_demo.py           # Demo & test script
└── README.md               # Bu dosya
```

## ⚡ Hızlı Başlangıç

### 1. Import ve Başlatma
```python
from ai.whale_tracker import WhaleTracker

# Whale tracker'ı başlat
tracker = WhaleTracker()
```

### 2. Manuel Scan
```python
# Tek seferlik whale tarama
result = tracker.manual_scan()
print(f"Tespit edilen whale: {result['whale_stats']['total_24h']}")
```

### 3. Sürekli Monitoring
```python
# Otomatik monitoring başlat
tracker.start_monitoring()

# ... sistem çalışır ...

# Durdur
tracker.stop_monitoring()
```

### 4. Aktif Sinyaller
```python
# Tüm aktif sinyaller
signals = tracker.get_active_signals()

# Belirli coin için
btc_signals = tracker.get_active_signals('BTC')

for signal in signals:
    print(f"{signal['symbol']}: {signal['signal_type']} ({signal['confidence']:.1%})")
```

## 🔧 Konfigürasyon

### API Keys (whale_config.py)
```python
# WhaleAlert.io API (ücretsiz plan mevcut)
WHALE_ALERT_API_KEY = "your_api_key_here"

# Etherscan API (ücretsiz)
ETHERSCAN_API_KEY = "your_etherscan_key"

# BSCScan API (ücretsiz) 
BSCSCAN_API_KEY = "your_bscscan_key"
```

### Whale Thresholds
```python
WHALE_THRESHOLD_BTC = 100        # 100+ BTC
WHALE_THRESHOLD_ETH = 1000       # 1000+ ETH
WHALE_THRESHOLD_USD = 1000000    # $1M+ USD
```

### Monitoring Settings
```python
CHECK_INTERVAL_SECONDS = 60      # Her 60 saniye kontrol
SIGNAL_CONFIDENCE_THRESHOLD = 0.6 # Min %60 güven
SIGNAL_DECAY_HOURS = 4           # 4 saatte expire
```

## 📊 Kullanım Örnekleri

### Basit Whale Monitoring
```python
from ai.whale_tracker import WhaleTracker

tracker = WhaleTracker()

# 24 saatlik monitoring
tracker.start_monitoring()
time.sleep(24 * 3600)  # 24 saat bekle
tracker.stop_monitoring()

# Sonuçları al
summary = tracker.get_whale_summary()
```

### Advanced Analytics
```python
# Detaylı whale analizi
analytics = tracker.get_whale_analytics(hours_back=24)

print(f"Total Volume: ${analytics['total_volume_usd']:,.0f}")
print(f"Whale Count: {analytics['total_whales']}")
print(f"Sentiment: {analytics['sentiment']['overall_sentiment']}")

# Exchange akışları
for exchange, flows in analytics['exchange_flows'].items():
    print(f"{exchange}: IN=${flows['inflow']:,.0f}, OUT=${flows['outflow']:,.0f}")
```

### Custom Signal Processing
```python
# Signal history
recent_signals = tracker.signal_generator.get_signal_history(
    symbol='BTC',
    hours_back=24
)

# Signal performance
performance = tracker.signal_generator.get_signal_performance()
print(f"Total signals: {performance['total_signals']}")
print(f"Avg confidence: {performance['avg_confidence']:.1%}")
```

## 🧪 Test & Demo

### Demo Script Çalıştırma
```bash
cd ai/whale_tracker
python whale_demo.py
```

### İnteraktif Test
```python
python whale_demo.py
# Demo sonunda 'y' seçerek interactive mode'a geçin
```

### Unit Tests
```python
# Demo script içindeki test fonksiyonları:
test_whale_signals()      # Sinyal üretimi test
test_whale_patterns()     # Pattern tespiti test  
benchmark_whale_tracker() # Performance test
```

## 📈 Trading Entegrasyonu

### Signal Processing
```python
def process_whale_signals():
    signals = tracker.get_active_signals()
    
    for signal in signals:
        if signal['strength'] in ['STRONG', 'VERY_STRONG']:
            symbol = signal['symbol']
            signal_type = signal['signal_type']
            confidence = signal['confidence']
            
            if signal_type == 'BULLISH' and confidence > 0.8:
                # BULLISH signal - Buy order
                print(f"🐂 Strong BUY signal for {symbol}")
                # place_buy_order(symbol, ...)
                
            elif signal_type == 'BEARISH' and confidence > 0.8:
                # BEARISH signal - Sell order  
                print(f"🐻 Strong SELL signal for {symbol}")
                # place_sell_order(symbol, ...)
```

### Risk Management
```python
def check_whale_risks():
    # Exchange'e büyük akış var mı?
    analytics = tracker.get_whale_analytics(hours_back=6)
    
    for exchange, flows in analytics.get('exchange_flows', {}).items():
        if flows['inflow'] > 50000000:  # $50M+ inflow
            print(f"⚠️ Risk: {exchange}'e büyük inflow")
            # Pozisyon azalt veya çık
```

## 🛠️ Customization

### Custom Whale Thresholds
```python
# Kendi threshold'larınızı ayarlayın
config.WHALE_THRESHOLD_BTC = 50    # 50+ BTC
config.WHALE_THRESHOLD_USD = 500000 # $500K+ USD
```

### Custom Notifications
```python
# Kendi notification handler'ınızı yazın
class CustomNotifier(WhaleNotifier):
    def _send_custom_notification(self, message):
        # Slack, Teams, vs. entegrasyonu
        pass
```

### Custom Analysis
```python
# Kendi analiz algoritmalarınızı ekleyin  
class CustomAnalyzer(WhaleAnalyzer):
    def custom_whale_pattern(self, whale_data):
        # Özel pattern logic'i
        pass
```

## ⚙️ Advanced Configuration

### API Rate Limiting
```python
API_RATE_LIMIT_PER_MINUTE = 50
REQUESTS_PER_SECOND = 1
CACHE_DURATION_MINUTES = 30
```

### Notification Settings
```python
ENABLE_WHALE_NOTIFICATIONS = True
NOTIFY_MINOR_WHALES = False      # Sadece büyük whales
NOTIFY_EXCHANGE_FLOWS = True     # Exchange hareketleri
NOTIFY_UNKNOWN_WALLETS = True    # Bilinmeyen wallets
```

### Signal Configuration
```python
GENERATE_SIGNALS = True
SIGNAL_CONFIDENCE_THRESHOLD = 0.6
SIGNAL_DECAY_HOURS = 4
AUTO_TRADING_ENABLED = False     # DİKKAT: Manuel kontrol önemli
```

## 📋 Performance Metrics

Whale Tracker performans metrikleri:

- **API Calls**: Dakika başına API çağrı sayısı
- **Whales Detected**: Tespit edilen whale sayısı  
- **Signals Generated**: Üretilen sinyal sayısı
- **Notifications Sent**: Gönderilen bildirim sayısı
- **Pattern Accuracy**: Pattern tespit doğruluğu
- **Response Time**: Ortalama yanıt süresi

```python
metrics = tracker.metrics
print(f"Uptime: {metrics['uptime_start']}")
print(f"Total Whales: {metrics['total_whales_detected']}")
print(f"Signal Count: {metrics['signals_generated']}")
```

## 🔒 Güvenlik

### API Key Security
- API keylerini environment variable'larda saklayın
- `.env` dosyası kullanın (git ignore'da)
- Production'da key rotation yapın

### Rate Limiting
- API limitlerine dikkat edin
- Cache kullanarak tekrar çağrıları azaltın
- Exponential backoff uygulayın

### Trading Safety
- Manual override her zaman mevcut
- Position size limiteri
- Stop-loss otomasyonu
- Kill switch mekanizması

## 🐛 Troubleshooting

### Common Issues

**API Key Hatası**
```
Error: WhaleAlert API key invalid
Solution: whale_config.py'da API key'i kontrol edin
```

**Rate Limit Aşımı**
```
Error: Rate limit exceeded
Solution: CHECK_INTERVAL_SECONDS'ı artırın
```

**No Data**
```
Warning: No whale data found
Solution: Threshold değerlerini düşürün veya timeframe artırın
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Detaylı log çıktısı
tracker = WhaleTracker()
```

## 📞 Support

Sorularınız için:
- GitHub Issues
- Documentation
- Example codes
- Community discussions

## 📄 License

Bu proje MIT lisansı altındadır. Ticari kullanım serbesttir.

---

🐋 **Happy Whale Hunting!** 

*Büyük balina hareketlerini yakalayın, erken avantaj elde edin!* 