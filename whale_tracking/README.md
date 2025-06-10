# Balina İzleme Sistemi

Bu proje, kripto para piyasalarında büyük işlemler yapan "balinalar"ı tespit eden ve takip eden bir sistemdir.

## Özellikler

- **Büyük İşlem Tespiti**: Belirli miktarların üzerindeki işlemleri tespit eder
- **Whale Analizi**: Whale davranış kalıplarını analiz eder
- **Telegram Bildirimleri**: Önemli whale aktivitelerini Telegram'dan bildirir
- **Real-time Monitoring**: Gerçek zamanlı whale takibi
- **Multi-Exchange Support**: Birden fazla borsa desteği
- **API Integration**: Whale verilerini API üzerinden sunar

## Dosya Yapısı

### whale_tracker/ klasörü:
- `whale_tracker.py`: Ana whale tracking sistemi
- `whale_analyzer.py`: Whale davranış analizi
- `whale_api.py`: Whale verileri API'si
- `whale_signals.py`: Whale sinyal sistemi
- `whale_notifications.py`: Telegram bildirimleri
- `whale_demo.py`: Demo ve test scripti
- `whale_config.py`: Whale sistemi konfigürasyonu
- `TELEGRAM_SETUP.md`: Telegram kurulum rehberi
- `README.md`: Detaylı proje dokümantasyonu

## Whale Tespit Kriterleri

### İşlem Büyüklüğü
- **Large**: $100K - $500K
- **Whale**: $500K - $1M
- **Mega Whale**: $1M+

### Analiz Parametreleri
- İşlem hacmi analizi
- Wallet davranış kalıpları
- Market impact değerlendirmesi
- Historical pattern analizi

## Kurulum

### 1. Temel Kurulum
```bash
pip install -r requirements.txt
```

### 2. Telegram Bot Kurulumu
1. `TELEGRAM_SETUP.md` dosyasını takip edin
2. Bot token ve chat ID'yi ayarlayın
3. `whale_config.py` dosyasında Telegram ayarlarını yapın

### 3. Konfigürasyon
`whale_config.py` dosyasında:
```python
# Whale tespit limitleri
WHALE_THRESHOLD = 500000  # $500K
MEGA_WHALE_THRESHOLD = 1000000  # $1M

# Telegram ayarları
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

# Monitoring ayarları
MONITORING_INTERVAL = 30  # saniye
ALERT_COOLDOWN = 300  # saniye
```

## Kullanım

### Whale Tracker Başlatma
```bash
cd whale_tracker
python whale_tracker.py
```

### Demo Çalıştırma
```bash
python whale_demo.py
```

### API Servisi
```bash
python whale_api.py
```

### Manuel Analiz
```python
from whale_tracker import WhaleAnalyzer

analyzer = WhaleAnalyzer()
whales = analyzer.detect_whale_activity("BTCUSDT")
print(whales)
```

## API Endpoints

### Whale Verileri
- `GET /whales`: Tüm whale aktiviteleri
- `GET /whales/{symbol}`: Belirli coin için whale aktiviteleri
- `GET /whale-stats`: Whale istatistikleri
- `GET /whale-alerts`: Aktif whale uyarıları

### Örnek API Kullanımı
```bash
curl http://localhost:8000/whales/BTCUSDT
```

## Telegram Bildirimleri

### Bildirim Türleri
- **🐋 Whale Alert**: Büyük işlem tespiti
- **📊 Market Impact**: Market etkisi analizi
- **⚠️ Unusual Activity**: Olağandışı aktivite
- **📈 Trend Alert**: Whale trend bildirimi

### Örnek Bildirim
```
🐋 WHALE ALERT - BTCUSDT
💰 Amount: $1,250,000
📊 Type: BUY
⏰ Time: 14:30:25
📈 Impact: +0.85%
```

## Whale Analiz Metrikleri

### Volume Analysis
- 24h whale volume
- Whale/total volume ratio
- Volume distribution

### Pattern Recognition
- Accumulation patterns
- Distribution patterns
- Market manipulation signals

### Risk Assessment
- Market impact scoring
- Volatility correlation
- Liquidity analysis

## Monitoring Dashboard

### Real-time Görünüm
- Aktif whale pozisyonları
- Günlük whale aktivite özeti
- Top whale wallets
- Market impact grafiği

### Historical Analysis
- Whale aktivite geçmişi
- Performance analizi
- Trend correlation
- Seasonal patterns

## Güvenlik ve Limitler

### API Rate Limits
- Binance API limitlerini respecter
- Request throttling
- Error handling ve retry logic

### Data Privacy
- Wallet adresi encryption
- Personal data protection
- GDPR compliance

## Uyarılar

- **Risk Yönetimi**: Whale aktiviteleri yatırım tavsiyesi değildir
- **Market Volatility**: Whale hareketleri volatilite artışına sebep olabilir
- **False Signals**: Sistem bazen yanlış sinyal verebilir
- **Legal Compliance**: Yasal düzenlemelere uygun kullanın

## Destek ve Geliştirme

### Log Analizi
```bash
tail -f whale_tracker/logs/whale_activity.log
```

### Debug Modu
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Monitoring
```python
from whale_tracker import WhaleTracker

tracker = WhaleTracker()
stats = tracker.get_performance_stats()
print(stats)
```

## Yol Haritası

- [ ] Machine Learning ile whale behavior prediction
- [ ] Cross-exchange whale tracking
- [ ] Advanced pattern recognition
- [ ] Portfolio impact analysis
- [ ] Social sentiment integration

Bu sistem ile kripto piyasalarında whale aktivitelerini yakından takip edebilir ve bilinçli yatırım kararları alabilirsiniz. 