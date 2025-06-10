# Test config dosyası
import os
from dotenv import load_dotenv

print("🚀 Test başlıyor...")

# .env dosyasını yükle
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
print(f"🔍 .env yolu: {env_path}")
print(f"📂 .env var mı: {os.path.exists(env_path)}")

load_dotenv(env_path)

# Binance API Ayarları
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

print(f"🔑 API Key: {API_KEY[:10] if API_KEY else 'YOK'}...")
print(f"🗝️ API Secret: {API_SECRET[:10] if API_SECRET else 'YOK'}...")

# Doğrudan değerler
if not API_KEY:
    API_KEY = "TJN1OEv4a0Ty3QtX9XEsxr1TMevNDlmxz0GqikI6KIVgHJz0nyPkYT1JrZgXaJdX"
    print("🔧 API Key manuel olarak ayarlandı")

if not API_SECRET:
    API_SECRET = "u0PD6kmtgLhkntywxkooFPm7wbUww8bkuUJGyztsFTB23ySXtt5Ku88ahbKkxzjh"
    print("🔧 API Secret manuel olarak ayarlandı")

print(f"✅ Final API Key Son 4: ...{API_KEY[-4:]}")
print(f"✅ Final API Secret Son 4: ...{API_SECRET[-4:]}")

# CCXT test
try:
    import ccxt
    exchange = ccxt.binance({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
        }
    })
    
    print("📊 Exchange bağlantısı kuruluyor...")
    balance = exchange.fetch_balance()
    print("✅ API bağlantısı başarılı!")
    print(f"💰 USDT Bakiye: {balance.get('USDT', {}).get('free', 0)}")
    
except Exception as e:
    print(f"❌ API bağlantı hatası: {e}") 