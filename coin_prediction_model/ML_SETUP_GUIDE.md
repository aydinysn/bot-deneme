# ML Fiyat Tahmin Sistemi Kurulum Rehberi

Bu rehber, Binance trading botunuza makine öğrenmesi tabanlı fiyat tahmin sisteminin nasıl kurulacağını açıklar.

## 🔧 Sistem Gereksinimleri

- **Python**: 3.13 (TensorFlow değil, scikit-learn tabanlı)
- **RAM**: Minimum 8GB (16GB önerilir)
- **Disk**: 5GB boş alan
- **İnternet**: Binance API erişimi

## 📦 Paket Kurulumu

### 1. ML Paketlerini Kurun

```bash
cd ai
pip install -r requirements_python313.txt
```

### 2. Kurulumu Doğrulayın

```bash
python -c "import sklearn, xgboost, lightgbm; print('✅ Tüm ML paketleri başarıyla yüklendi')"
```

## 🚀 Hızlı Başlangıç

### 1. İlk 10 Coin İçin Test Eğitimi

```bash
cd ai
python train_first_10.py
```

Bu komut yaklaşık 15-30 dakika sürer ve sisteminizi test eder.

### 2. Hızlı Tahmin Testi

Eğitim tamamlandıktan sonra:

```bash
python quick_prediction.py BTCUSDT
```

### 3. Tüm Coinler İçin Eğitim (Opsiyonel)

```bash
python train_all_coins.py
```

⚠️ **Uyarı**: Bu işlem 1-2 saat sürebilir.

## 📊 Sistem Mimarisi

### ML Modelleri

1. **Random Forest**: Hızlı ve güvenilir
2. **XGBoost**: Yüksek performanslı gradient boosting
3. **LightGBM**: Hızlı ve hafıza verimli
4. **Gradient Boosting**: Scikit-learn implementasyonu
5. **Ensemble**: Tüm modellerin ağırlıklı kombinasyonu

### Özellik Mühendisliği (25+ Teknik Gösterge)

- **Hareketli Ortalamalar**: SMA/EMA (5, 10, 20, 50, 100, 200)
- **Momentum**: RSI (14, 21), MACD, Stochastic, Williams %R
- **Volatilite**: Bollinger Bands, ATR, standart sapma
- **Volume**: Volume ortalamaları, oran analizi
- **Trend**: ROC, momentum göstergeleri
- **Zaman**: Saat, gün, hafta sonu faktörleri

## ⚙️ Konfigürasyon

### ML Ayarları (config.py)

```python
# ML Model Configuration
ML_ENABLED = True
ML_MODEL_TYPE = 'ensemble'  # 'random_forest', 'xgboost', 'lightgbm', 'ensemble'
ML_SEQUENCE_LENGTH = 60     # 60 saatlik veri penceresi

# Tahmin Ayarları
ML_PREDICTION_WEIGHT = 0.3     # Trading sinyalindeki ağırlığı
ML_MIN_CONFIDENCE = 0.6        # Minimum güven skoru
ML_SIGNAL_THRESHOLD = 0.7      # Sinyal eşiği
```

## 🔄 Kullanım Örnekleri

### 1. Tek Coin Tahmini

```python
from ml_models.model_trainer import ModelTrainer

trainer = ModelTrainer()
predictor = trainer.load_trained_model('BTCUSDT')

# Güncel veriyi al ve tahmin yap
df = await trainer.get_historical_data('BTCUSDT')
result = predictor.predict(df)

print(f"Tahmin: ${result['prediction']:.4f}")
print(f"Güven: {result['confidence']:.1%}")
```

### 2. Trading Sinyali Entegrasyonu

```python
from trading_with_ml import MLTradingSignals

ml_signals = MLTradingSignals()
signal = await ml_signals.get_ml_signal('ETHUSDT')

if signal['should_trade']:
    direction = signal['direction']  # 'LONG' veya 'SHORT'
    level = signal['signal_level']   # 'STRONG', 'MEDIUM', 'WEAK'
    confidence = signal['confidence'] # 0.0 - 1.0
```

### 3. Çoklu Coin Analizi

```bash
python trading_with_ml.py
```

## 📈 Performans Metrikleri

### Model Değerlendirme

- **MAPE (Mean Absolute Percentage Error)**: Ana metrik
- **MAE (Mean Absolute Error)**: Mutlak hata
- **RMSE (Root Mean Square Error)**: Kök ortalama kare hata

### Beklenen Performans

- **MAPE**: %2-8 (coin'e göre değişir)
- **Güven Skoru**: 0.6-0.9
- **Tahmin Süresi**: <1 saniye
- **Model Boyutu**: 1-5MB per coin

## 🔧 Sorun Giderme

### Sık Karşılaşılan Hatalar

#### 1. "ModuleNotFoundError: No module named 'xgboost'"

```bash
pip install xgboost lightgbm scikit-learn
```

#### 2. "Model henüz eğitilmedi"

```bash
cd ai
python train_first_10.py  # veya
python train_all_coins.py
```

#### 3. "Yetersiz veri"

Coin için en az 100 saatlik veri gereklidir. Yeni listelenen coinler için bekleyin.

#### 4. Yavaş Eğitim

- RAM artırın (16GB önerilir)
- Batch boyutunu azaltın
- Daha az coin ile test yapın

### Log Kontrolü

```bash
tail -f logs/ml_training.log
```

## 📊 Model Yönetimi

### Modelleri Kontrol Etme

```python
from ml_models.model_trainer import ModelTrainer

trainer = ModelTrainer()
summary = trainer.get_training_summary()

print(f"Eğitilmiş modeller: {len(summary['available_models'])}")
print(f"Başarı oranı: {summary['training_status']['success_rate']:.1f}%")
```

### Model Yenileme

```bash
# Tek model yenileme
python -c "from ml_models.model_trainer import ModelTrainer; import asyncio; asyncio.run(ModelTrainer().retrain_model('BTCUSDT'))"

# Tüm modelleri yenileme (24 saat sonra)
python train_all_coins.py
```

### Model Dosyaları

- **Konum**: `ai/ml_models/saved_models/`
- **Format**: `{SYMBOL}_ml_model.pkl`
- **Boyut**: 1-5MB per model
- **İçerik**: Model + preprocessor + metadata

## 🎯 Optimizasyon İpuçları

### 1. Model Seçimi

- **Hızlı tahmin**: `random_forest`
- **En iyi doğruluk**: `ensemble`
- **Az RAM**: `lightgbm`
- **Genel kullanım**: `xgboost`

### 2. Parametre Ayarlama

```python
# Daha agresif tahminler için
ML_SIGNAL_THRESHOLD = 0.5
ML_MIN_CONFIDENCE = 0.5

# Daha konservatif için
ML_SIGNAL_THRESHOLD = 0.8
ML_MIN_CONFIDENCE = 0.7
```

### 3. Özellik Optimizasyonu

Yavaş eğitim için `data_preprocessor.py`'de bazı özellikleri kapatabilirsiniz:

```python
# Daha az özellik için
for period in [14]:  # Sadece 14 yerine [14, 21]
    # RSI hesaplaması
```

## 🔄 Otomatik Güncelleme

### Cron Job Kurulumu (Linux/Mac)

```bash
# Her gün saat 03:00'da modelleri güncelle
crontab -e

# Şu satırı ekleyin:
0 3 * * * cd /path/to/BinanceBot/ai && python train_all_coins.py >> logs/auto_retrain.log 2>&1
```

### Windows Task Scheduler

1. Task Scheduler'ı açın
2. "Create Basic Task" seçin
3. Günlük çalışacak şekilde ayarlayın
4. Action: `python train_all_coins.py`

## 📊 Performans İzleme

### Real-time Monitoring

```python
# Her 10 dakikada tahmin al ve logla
import schedule
import time

def log_prediction():
    result = predictor.predict(df)
    print(f"[{datetime.now()}] Tahmin: {result['prediction']:.4f}")

schedule.every(10).minutes.do(log_prediction)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### Performans Raporları

```bash
# Training sonuçlarını görüntüle
ls training_results_*.json

# En son sonuçları oku
python -c "import json; print(json.load(open('training_results_latest.json', 'r'))['successful_coins'])"
```

## 🚨 Önemli Notlar

### Risk Uyarıları

1. **ML tahminleri garanti değildir**
2. **Risk yönetimi her zaman önceliklidir**
3. **Backtesting yaparak performansı doğrulayın**
4. **Çok büyük pozisyonlar almayın**

### Limitasyonlar

1. **Ani piyasa değişiklikleri** tahmin edilemez
2. **Düşük volume coinlerde** doğruluk azalır
3. **Yeni listelenen coinler** için veri yetersiz
4. **Aşırı volatil dönemlerde** performans düşer

## 🆘 Destek

### Problem Bildirimi

Issues kısmından şu bilgilerle birlikte rapor edin:

1. Python versiyonu
2. Hata mesajı
3. Son çalıştırılan komut
4. Log dosyaları (`logs/` klasöründen)

### Performans Optimizasyonu

Yavaş çalışıyorsa:

1. RAM kullanımını kontrol edin
2. Disk I/O'yu izleyin  
3. Batch boyutunu azaltın
4. Daha az özellik kullanın

Bu rehber sisteminizi başarıyla kuracaktır. Herhangi bir sorun yaşarsanız, adım adım takip ederek çözebilirsiniz. 