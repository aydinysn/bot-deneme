# 🐋 Whale Position Tracker

Bu proje, kripto para piyasalarında büyük hacimli işlemler yapan "balinalar"ın pozisyonlarını takip eden ve hangi coinlerde long/short pozisyonları açtıklarını bildiren bir sistemdir.

## ✨ Özellikler

### 🔍 Balina Tespiti
- **$100K+** büyük işlem tespiti
- **$500K+** balina sınıflandırması
- **$1M+** mega balina kategorisi
- Gerçek zamanlı pozisyon analizi

### 📊 Pozisyon Analizi
- Long/Short pozisyon belirleme
- Güven skoru hesaplama
- Aktivite seviyesi değerlendirmesi
- Trend yönü analizi

### 📱 Telegram Bildirimleri
- Anlık balina pozisyon alertleri
- Günlük aktivite özetleri
- Detaylı işlem bilgileri
- Smart cooldown sistemi

### 📈 İstatistikler
- 24 saatlik balina aktiviteleri
- Coin bazında volume analizi
- Long/Short oran takibi
- Top balina coinleri listesi

## 🚀 Hızlı Başlangıç

### 1. Kurulum
```bash
pip install -r requirements.txt
```

### 2. Konfigürasyon
`config.py` dosyasını düzenleyin:

```python
# Binance API Ayarları
API_KEY = "your_binance_api_key_here"
API_SECRET = "your_binance_api_secret_here"

# Telegram Bildirim Ayarları
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token_here"
TELEGRAM_CHAT_ID = "your_telegram_chat_id_here"
```

### 3. Çalıştırma
```bash
python whale_position_tracker.py
```

## ⚙️ Konfigürasyon Seçenekleri

### Whale Tespit Parametreleri
```python
LARGE_TRADE_THRESHOLD = 100000      # $100K minimum işlem büyüklüğü
WHALE_THRESHOLD = 500000            # $500K balina limiti
MEGA_WHALE_THRESHOLD = 1000000      # $1M mega balina limiti
```

### Monitoring Ayarları
```python
SCAN_INTERVAL = 30                  # Tarama aralığı (saniye)
API_DELAY = 2                       # API çağrıları arası bekleme
TRADES_LIMIT = 500                  # Her taramada kontrol edilecek işlem sayısı
```

### Alert Ayarları
```python
ALERT_CONFIDENCE_THRESHOLD = 0.7    # Minimum güven skoru
ALERT_ACTIVITY_LEVELS = ['HIGH', 'EXTREME']  # Bildirim seviyeleri
ALERT_COOLDOWN = 300                # Alert arası minimum süre (saniye)
```

### Takip Edilen Coinler
```python
MONITORING_SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'SOL/USDT',
    'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT',
    # ... daha fazla coin ekleyebilirsiniz
]
```

## 📋 Kullanım Senaryoları

### 1. Anlık Takip
```bash
# Sürekli monitoring için
python whale_position_tracker.py
```

### 2. Programmatik Kullanım
```python
from whale_position_tracker import WhalePositionTracker

# Tracker oluştur
tracker = WhalePositionTracker()

# Belirli bir coin için whale pozisyonlarını kontrol et
positions = tracker.detect_whale_positions('BTC/USDT')
print(positions)

# Günlük özet al
summary = tracker.get_whale_summary()
print(summary)
```

### 3. Custom Configuration
```python
# Özel ayarlarla başlat
tracker = WhalePositionTracker(
    api_key="your_api_key",
    api_secret="your_api_secret",
    telegram_token="your_telegram_token",
    telegram_chat_id="your_chat_id"
)
```

## 📊 Bildirim Örnekleri

### Whale Position Alert
```
🚨 BALİNA POZİSYON TESPİTİ

🪙 Coin: BTC/USDT
🟢 Pozisyon: LONG
💰 Toplam Hacim: $2,450,000
📊 Güven: 85.2%
🔥 Aktivite: HIGH
📈 İşlem Sayısı: 8

💎 En Büyük İşlem:
└ Değer: $1,200,000
└ Tip: WHALE
└ Zaman: 14:23:15

⏰ Tespit Zamanı: 14:23:45
```

### Günlük Özet
```
🚀 GÜNLÜK BALİNA ÖZETİ

📊 Genel Sentiment: BULLISH
🪙 Aktif Coin: 12/20

🏆 TOP 5 BALİNA AKTİVİTESİ:
1. 🟢 BTC/USDT
   💰 $8,750,000 | 📊 25 işlem
2. 🟢 ETH/USDT
   💰 $5,230,000 | 📊 18 işlem
3. 🔴 SOL/USDT
   💰 $3,120,000 | 📊 12 işlem

⏰ Rapor Zamanı: 10/06/2025 23:59
```

## 🔍 Analiz Metodolojisi

### Pozisyon Belirleme
1. **Trade Direction**: Buy/Sell analizi
2. **Price Proximity**: Güncel fiyata yakınlık
3. **Volume Weighting**: Hacim ağırlıklı hesaplama
4. **Confidence Scoring**: Güven skoru atama

### Aktivite Seviyeleri
- **LOW**: Standart aktivite
- **MEDIUM**: Orta seviye balina aktivitesi
- **HIGH**: Yüksek balina aktivitesi (alert)
- **EXTREME**: Aşırı aktivite (urgent alert)

### Güven Skoru Hesaplama
```
Confidence = Dominant_Side_Volume / Total_Volume
```

## 🛡️ Güvenlik ve Limitler

### API Rate Limiting
- Binance rate limitlerini respecter
- Akıllı request throttling
- Automatic retry mechanism

### Error Handling
- Network hatalarına karşı dayanıklılık
- Graceful degradation
- Comprehensive logging

### Data Privacy
- API anahtarları güvenli saklama
- Log dosyalarında hassas veri yok
- GDPR uyumlu veri işleme

## 📁 Dosya Yapısı

```
whale_position_tracker/
├── whale_position_tracker.py   # Ana tracker scripti
├── config.py                   # Konfigürasyon dosyası
├── requirements.txt            # Python dependencies
├── README.md                   # Bu dosya
└── whale_positions.log         # Log dosyası (oluşturulur)
```

## 🔧 Troubleshooting

### API Connection Issues
```bash
# API anahtarlarını kontrol edin
# Binance futures permission aktif olmalı
# Network bağlantısını test edin
```

### Telegram Notifications
```bash
# Bot token doğru mu?
# Chat ID doğru mu?
# Bot'a mesaj izni var mı?
```

### Performance Issues
```bash
# SCAN_INTERVAL'ı artırın
# MONITORING_SYMBOLS listesini azaltın
# API_DELAY'i artırın
```

## 🎯 İleri Düzey Kullanım

### Custom Whale Logic
```python
class CustomWhaleTracker(WhalePositionTracker):
    def _classify_whale_size(self, trade_value):
        # Özel balina sınıflandırma logic'i
        if trade_value >= 2000000:  # $2M
            return 'SUPER_WHALE'
        return super()._classify_whale_size(trade_value)
```

### Data Export
```python
# İstatistikleri JSON olarak kaydet
summary = tracker.get_whale_summary()
with open('whale_stats.json', 'w') as f:
    json.dump(summary, f, default=str)
```

### Integration Examples
```python
# Trading bot ile entegrasyon
if tracker._should_alert(analysis):
    # Trading sinyali gönder
    send_trading_signal(analysis['symbol'], analysis['dominant_side'])
```

## ⚠️ Uyarılar

- **Investment Advice**: Bu sistem yatırım tavsiyesi değildir
- **Market Risk**: Whale aktiviteleri volatilite artışına sebep olabilir
- **False Signals**: Sistem bazen yanlış sinyal verebilir
- **Legal Compliance**: Yasal düzenlemelere uygun kullanın

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## 📞 Destek

- Issues: GitHub Issues bölümünü kullanın
- Documentation: README dosyasını inceleyin
- Community: Telegram grubuna katılın

---

**Happy Whale Tracking! 🐋📊**

*Bu proje ile kripto piyasalarında balina hareketlerini yakından takip edebilir ve bilinçli trading kararları alabilirsiniz.* 