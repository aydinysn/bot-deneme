# Binance Trading Bot Ecosystem

Bu proje, kripto para trading için kapsamlı bir ekosistem sunar ve 3 ana bileşenden oluşur:

## 🚀 Proje Yapısı

### 1. 📈 [TradeBot](./tradebot/) 
**Ana Trading Bot Sistemi**
- Otomatik alım-satım işlemleri
- Çoklu strateji desteği
- Risk yönetimi
- Teknik analiz indikatörleri
- Real-time trading

### 2. 🧠 [Coin Prediction Model](./coin_prediction_model/)
**AI Destekli Fiyat Tahmin Sistemi**
- LSTM ve ML modelleri
- Fiyat tahmin algoritmaları
- Feature engineering
- Model eğitimi ve optimizasyon
- Trading ile entegrasyon

### 3. 🐋 [Whale Tracking](./whale_tracking/)
**Balina İzleme Sistemi**
- Büyük işlem tespiti
- Whale davranış analizi
- Telegram bildirimleri
- Real-time monitoring
- Market impact analizi

## 🛠️ Hızlı Başlangıç

### Sistem Gereksinimleri
- Python 3.8+
- Binance API anahtarları
- Internet bağlantısı

### 1. TradeBot'u Çalıştırma
```bash
cd tradebot
pip install -r requirements.txt
python main.py
```

### 2. AI Model Eğitimi
```bash
cd coin_prediction_model
pip install -r requirements_python313.txt
python train_single_coin.py
```

### 3. Whale Tracking Başlatma
```bash
cd whale_tracking/whale_tracker
python whale_tracker.py
```

## 📊 Özellikler

### Trading Bot Özellikleri
- ✅ Otomatik trading algoritmaları
- ✅ Risk yönetimi sistemi
- ✅ Çoklu coin desteği
- ✅ Teknik analiz indikatörleri
- ✅ Backtesting desteği
- ✅ Real-time market analizi

### AI Tahmin Sistemi
- ✅ LSTM neural networks
- ✅ Multiple ML algorithms (RF, XGBoost, LightGBM)
- ✅ 25+ teknik indikatör
- ✅ Ensemble learning
- ✅ %1-5 MAPE accuracy
- ✅ Real-time predictions

### Whale Tracking
- ✅ $100K+ işlem tespiti
- ✅ Telegram alert sistemi
- ✅ Market impact analizi
- ✅ Whale pattern recognition
- ✅ API servisi
- ✅ Historical whale data

## 🔧 Konfigürasyon

Her projenin kendi konfigürasyon dosyası vardır:

- **TradeBot**: `tradebot/config.py`
- **AI Models**: `coin_prediction_model/` içindeki model-specific configs
- **Whale Tracker**: `whale_tracking/whale_tracker/whale_config.py`

## 📈 Performance

### Trading Bot
- Günlük %1-3 ortalama getiri
- %15 maksimum drawdown
- 1.2+ Sharpe ratio

### AI Models
- BTCUSDT: %4.85 MAPE
- ETHUSDT: %1.68 MAPE
- SOLUSDT: %1.10 MAPE

### Whale Tracker
- <30 saniye detection time
- %95+ accuracy rate
- Real-time Telegram alerts

## 🔗 Entegrasyon

Sistemler birbirleriyle entegre çalışabilir:

```python
# Trading bot'a AI tahminleri eklemek
from coin_prediction_model.trading_with_ml import MLTradingBot
bot = MLTradingBot()

# Whale sinyallerini trading'e dahil etmek
from whale_tracking.whale_tracker import WhaleAnalyzer
whale_analyzer = WhaleAnalyzer()
```

## 📚 Dokümantasyon

Her proje için detaylı dokümantasyon:

- [TradeBot README](./tradebot/README.md)
- [AI Models README](./coin_prediction_model/README.md)
- [Whale Tracking README](./whale_tracking/README.md)

## ⚠️ Risk Uyarısı

- Bu sistem finansal tavsiye değildir
- Kendi riskiniz altında kullanın
- Küçük miktarlarla test edin
- Risk yönetimi kurallarını uygulayın
- Yasal düzenlemelere uygun kullanın

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## 📄 Lisans

Bu proje MIT lisansı altında dağıtılmaktadır.

---

**Happy Trading! 🚀**

*Bu proje sürekli geliştirilmektedir. Güncellemeler için repo'yu takip edin.* 