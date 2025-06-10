# 🤖 Telegram Bot Kurulum Rehberi

Whale Tracker sinyallerini Telegram'a göndermek için aşağıdaki adımları takip edin.

## 📋 Gereklilikler

- Telegram hesabı
- Python `requests` kütüphanesi (zaten yüklü)

## 🤖 1. Telegram Bot Oluşturma

### Adım 1: BotFather ile Bot Oluşturun
1. Telegram'da [@BotFather](https://t.me/botfather) botunu bulun
2. `/start` komutunu gönderin
3. `/newbot` komutunu gönderin
4. Bot için bir isim girin (örn: "My Whale Tracker")
5. Bot için bir username girin (örn: "my_whale_tracker_bot")
6. BotFather size bir **BOT TOKEN** verecek (örn: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Adım 2: Chat ID'yi Bulun

#### Kişisel Chat için:
1. Oluşturduğunuz bot ile konuşmaya başlayın
2. `/start` mesajı gönderin
3. Aşağıdaki URL'yi tarayıcınızda açın:
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
   ```
4. JSON yanıtında `"chat":{"id":123456789}` değerini bulun
5. Bu sayı sizin **CHAT ID**'niz

#### Grup Chat için:
1. Botu gruba ekleyin
2. Grupta `/start@botusername` mesajı gönderin
3. Yukarıdaki URL'yi kullanarak Chat ID'yi bulun
4. Grup ID'leri genelde negatif sayıdır (örn: `-123456789`)

## ⚙️ 2. Whale Tracker Konfigürasyonu

### whale_config.py Dosyasını Düzenleyin:

```python
# ================== TELEGRAM BOT SETTINGS ==================

# Bot Token ve Chat ID'yi buraya girin
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # BotFather'dan aldığınız token
TELEGRAM_CHAT_ID = "123456789"                              # Chat ID'nizi girin

# Telegram bildirimlerini aktif et
TELEGRAM_ENABLED = True

# Hangi bildirimlerin gönderileceğini seçin
TELEGRAM_SEND_WHALE_MOVEMENTS = True    # Whale hareketleri
TELEGRAM_SEND_SIGNALS = True            # Trading sinyalleri  
TELEGRAM_SEND_PATTERNS = True           # Pattern tespitleri
TELEGRAM_SEND_ALERTS = True             # Market alertleri

# Mesaj ayarları
TELEGRAM_PARSE_MODE = "Markdown"        # Markdown veya HTML
TELEGRAM_DISABLE_PREVIEW = True         # Link preview'ları kapat
TELEGRAM_SEND_ONLY_STRONG = False       # Sadece güçlü sinyaller (True/False)
```

## 🧪 3. Test Etme

### Test Kodunu Çalıştırın:

```python
from ai.whale_tracker import WhaleNotifier

# Notifier'ı başlat
notifier = WhaleNotifier()

# Telegram bağlantısını test et
result = notifier.test_telegram_connection()

if result:
    print("✅ Telegram bağlantısı başarılı!")
else:
    print("❌ Telegram bağlantısı başarısız!")

# Bot bilgilerini kontrol et
bot_info = notifier.get_telegram_bot_info()
print(f"Bot Info: {bot_info}")
```

### Manuel Test Mesajı:

```python
# Test mesajı gönder
test_message = """🧪 *TEST MESAJI*

Bu bir test mesajıdır.
Whale Tracker Telegram entegrasyonu çalışıyor! ✅

⏰ Zaman: `{datetime.now().strftime('%H:%M:%S')}`"""

success = notifier._send_telegram_notification(test_message)
```

## 🚀 4. Whale Tracker ile Kullanım

### Tam Entegrasyon:

```python
from ai.whale_tracker import WhaleTracker

# Whale tracker'ı başlat
tracker = WhaleTracker()

# Monitoring'i başlat (otomatik Telegram bildirimleri gelecek)
tracker.start_monitoring()

# Manuel scan (test için)
result = tracker.manual_scan()

# Durdur
tracker.stop_monitoring()
```

## 📱 5. Telegram Mesaj Örnekleri

### Whale Hareketi Bildirimi:
```
🐋 WHALE HAREKET 🐂

💰 Coin: BTC
📊 Miktar: 250.50 BTC ($27,555,000)
🎯 Signal: BULLISH 🐂
💪 Güç: MAJOR 🔥🔥
🎲 Güven: 78.5%

📍 Transfer:
↗️ Gönderen: unknown...
↘️ Alan: binance...

💡 Önerilen: BUY
⏰ Zaman: 14:35:22
```

### Trading Sinyali:
```
📈 WHALE SİNYALLER ÜRETİLDİ

🎯 Toplam Sinyal: 3

Sinyaller:
🐂 BTC: BULLISH (82.1%) - STRONG
🐻 ETH: BEARISH (71.3%) - MODERATE
🔄 BNB: NEUTRAL (45.2%) - WEAK

⏰ Zaman: 14:36:15
```

### Pattern Tespiti:
```
🔍 WHALE PATTERN TESPİT

🎯 Güven Skoru: 85.2%

📊 Tespit Edilen Patternler:
• 🟢 Accumulation (Toplama)
• 🚀 Exchange Exodus

💡 Tavsiye: Potansiyel fiyat artışına hazır olun

⏰ Zaman: 14:37:45
```

## 🔧 6. İleri Seviye Ayarlar

### Sadece Önemli Sinyaller:
```python
# Sadece güçlü sinyaller için bildirim
TELEGRAM_SEND_ONLY_STRONG = True

# Minimum güven eşiği
SIGNAL_CONFIDENCE_THRESHOLD = 0.8  # %80+

# Sadece büyük whale'ler
NOTIFY_MINOR_WHALES = False
```

### Özel Mesaj Formatı:
```python
# HTML format kullan
TELEGRAM_PARSE_MODE = "HTML"

# Mesajlarda bold, italic kullanımı:
# Markdown: *bold*, _italic_, `code`
# HTML: <b>bold</b>, <i>italic</i>, <code>code</code>
```

### Rate Limiting:
```python
# Çok fazla mesaj gönderilmesini engelle
MIN_SIGNAL_INTERVAL = 300  # 5 dakika ara
CHECK_INTERVAL_SECONDS = 60  # 1 dakika check
```

## 🛠️ 7. Sorun Giderme

### Yaygın Hatalar:

#### "Telegram bot token not configured"
- `whale_config.py`'da `TELEGRAM_BOT_TOKEN` kontrol edin
- Token'ın doğru kopyalandığından emin olun

#### "Telegram chat ID not configured" 
- Chat ID'nin doğru girildiğinden emin olun
- Grup ID'leri negatif olabilir (-)

#### "Telegram notification failed: 403"
- Bot'u chat'e eklemediğiniz
- Bot'la konuşmaya başlamamışsınız
- Bot'un mesaj gönderme izni yok

#### "Telegram notification failed: 400"
- Mesaj formatı hatalı (Markdown/HTML)
- Chat ID yanlış format

### Debug Modu:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Detaylı log çıktısı göreceksiniz
notifier = WhaleNotifier()
```

## 📊 8. Performance

### Mesaj Limitleri:
- Telegram: Saniyede 30 mesaj
- Bot API: Dakikada 20 mesaj/grup
- Uzun mesajlar (4096 karakter) otomatik kesilir

### Optimizasyon:
```python
# Mesaj birleştirme
TELEGRAM_BATCH_SIGNALS = True  # Birden fazla sinyali tek mesajda gönder

# Filtering
TELEGRAM_MIN_WHALE_USD = 5000000  # $5M+ whale'ler için bildirim
```

## 🚨 9. Güvenlik

### Önemli Notlar:
- Bot token'ınızı kimseyle paylaşmayın
- Token'ı `.env` dosyasında saklayın
- Production'da environment variable kullanın
- Chat ID'yi private tutun

### Environment Variables:
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

```python
import os
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_default_token')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'your_default_chat_id')
```

## 🎯 10. Örnekler

### Basit Kullanım:
```python
# 1. Bot token ve chat ID'yi config'e girin
# 2. Test edin
# 3. Whale tracker'ı başlatın

from ai.whale_tracker import WhaleTracker
tracker = WhaleTracker()
tracker.start_monitoring()
```

### Manuel Kontrol:
```python
# Manuel whale tarama ve Telegram bildirimi
result = tracker.manual_scan()
if result['whale_stats']['total_24h'] > 0:
    print("Whale tespit edildi, Telegram'a bildirim gönderildi!")
```

### Özel Bildirim:
```python
# Kendi mesajınızı gönderin
notifier = tracker.notifier
custom_message = "🔥 Manuel analiz sonucu: BTC güçlü accumulation!"
notifier._send_telegram_notification(custom_message)
```

---

🎉 **Tebrikler!** 

Artık Whale Tracker sinyalleri otomatik olarak Telegram'a gönderilecek!

📞 **Sorun yaşarsanız:**
- Log dosyalarını kontrol edin
- Debug mode'u açın  
- Test fonksiyonlarını kullanın
- Bot'un yetkilerini kontrol edin

🐋 **Happy Whale Hunting via Telegram!** 