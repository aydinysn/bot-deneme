# Coin Fiyat Tahmin Modeli

Bu proje, makine öğrenmesi ve derin öğrenme tekniklerini kullanarak kripto para fiyat tahminleri yapan AI modellerini içerir.

## Özellikler

- **LSTM Neural Networks**: Fiyat tahminleri için LSTM modelleri
- **Multi-Coin Training**: Çoklu coin eğitimi desteği
- **Feature Engineering**: Gelişmiş özellik mühendisliği
- **Backtesting**: Model performans testi
- **Real-time Predictions**: Gerçek zamanlı tahmin yapma

## Dosya Yapısı

- `predict_price.py`: Tek coin fiyat tahmin scripti
- `train_single_coin.py`: Tek coin için model eğitimi
- `train_all_coins.py`: Tüm coinler için toplu eğitim
- `train_first_10.py`: İlk 10 coin için eğitim
- `trading_with_ml.py`: ML ile trading entegrasyonu
- `quick_prediction.py`: Hızlı tahmin scripti
- `lstm_integration_example.py`: LSTM entegrasyon örneği
- `ml_integration_example.py`: ML entegrasyon örneği
- `LSTM_SETUP_GUIDE.md`: LSTM kurulum rehberi
- `ML_SETUP_GUIDE.md`: ML kurulum rehberi
- `feature_benefits.md`: Özellik faydaları
- `advanced_features.md`: Gelişmiş özellikler
- `feature_roadmap.md`: Özellik yol haritası
- `training_results_*.json`: Eğitim sonuçları
- `ml_models/`: Eğitilmiş modeller
- `requirements_python313.txt`: Python 3.13 için gereksinimler

## Model Türleri

### LSTM (Long Short-Term Memory)
- Zaman serisi verilerinde uzun vadeli bağımlılıkları öğrenir
- Fiyat hareketlerindeki kalıpları tespit eder
- Volatilite ve trend analizinde etkilidir

### Features (Özellikler)
- Teknik indikatörler (RSI, MACD, Bollinger Bands)
- Volume analizi
- Market mikroyapısı
- Sentiment analizi
- Makroekonomik faktörler

## Kurulum

1. Python 3.13+ gereklidir
```bash
pip install -r requirements_python313.txt
```

2. Veri setini hazırlayın ve model eğitimini başlatın:
```bash
python train_single_coin.py
```

3. Tahmin yapmak için:
```bash
python predict_price.py
```

## Model Eğitimi

### Tek Coin Eğitimi
```bash
python train_single_coin.py --coin BTCUSDT --epochs 100
```

### Çoklu Coin Eğitimi
```bash
python train_all_coins.py
```

### Hızlı Test
```bash
python quick_prediction.py
```

## Performans Metrikleri

- **RMSE**: Root Mean Square Error
- **MAE**: Mean Absolute Error
- **MAPE**: Mean Absolute Percentage Error
- **R²**: Determination Coefficient
- **Sharpe Ratio**: Risk-adjusted returns

## Trading Entegrasyonu

ML modellerini trading bot'unuzla entegre etmek için:
```python
from trading_with_ml import MLTradingBot

bot = MLTradingBot()
bot.start_trading()
```

## Model Kaydetme ve Yükleme

Eğitilmiş modeller `ml_models/saved_models/` klasöründe saklanır:
- Model ağırlıkları
- Preprocessing parametreleri
- Feature scaling bilgileri
- Training istatistikleri

## Uyarı

- Bu modeller geçmiş verilere dayanır ve gelecek performansı garanti etmez
- Finansal kararlarda kullanmadan önce thorough backtesting yapın
- Risk yönetimi kurallarını her zaman uygulayın
- Bu proje finansal tavsiye değildir 