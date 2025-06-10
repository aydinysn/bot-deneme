# Binance Trade Bot

Bu proje, Binance kripto para borsasında otomatik alım-satım işlemleri gerçekleştiren bir trading bot'tur.

## Özellikler

- **Otomatik Trading**: Çeşitli strateji ve indikatörlere dayalı otomatik alım-satım
- **Risk Yönetimi**: Gelişmiş risk yönetimi ve pozisyon boyutlandırma
- **Teknik İndikatörler**: RSI, Bollinger Bands, Volume Profile ve daha fazlası
- **Multi-Timeframe Analiz**: Farklı zaman dilimlerinde analiz
- **Logging**: Detaylı işlem kayıtları

## Dosya Yapısı

- `main.py`: Ana trading bot dosyası
- `config.py`: Konfigürasyon ayarları
- `coins.json`: İşlem yapılacak coin listesi
- `utils/`: Yardımcı fonksiyonlar
  - `risk_management.py`: Risk yönetimi
  - `position_sizing.py`: Pozisyon boyutlandırma
  - `logging_helper.py`: Log yardımcıları
  - `coin_manager.py`: Coin yönetimi
- `strategies/`: Trading stratejileri
  - `rsi_divergence.py`: RSI divergence stratejisi
  - `multi_timeframe.py`: Multi-timeframe stratejisi
  - `market_structure.py`: Market yapısı analizi
  - `bollinger_bands.py`: Bollinger Bands stratejisi
- `indicators/`: Teknik indikatörler
  - `technical.py`: Teknik analiz fonksiyonları
  - `volume_profile.py`: Volume profil analizi

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `config.py` dosyasında API anahtarlarınızı ayarlayın
3. `coins.json` dosyasında işlem yapmak istediğiniz coinleri belirleyin
4. Bot'u çalıştırın:
```bash
python main.py
```

## Güvenlik

- API anahtarlarınızı asla paylaşmayın
- Test modunda çalıştırmadan önce küçük miktarlarla test edin
- Risk yönetimi ayarlarını dikkatlice yapılandırın

## Uyarı

Bu bot finansal tavsiye değildir. Kendi riski altında kullanın. 