# === Whale Position Tracker Configuration ===

# Binance API Ayarları (Public API için - Private key'ler kullanılmayacak)
API_KEY = ""  # Public API için gerekli değil
API_SECRET = ""  # Public API için gerekli değil

# Telegram Bildirim Ayarları
TELEGRAM_BOT_TOKEN = "7653317241:AAH2t8-C4qBtzi9-zEnFF9mJ0csCFJ8iyVA"
TELEGRAM_CHAT_ID = "924928056"

# Whale Tespit Parametreleri
LARGE_TRADE_THRESHOLD = 100000      # $100K minimum işlem büyüklüğü
WHALE_THRESHOLD = 500000            # $500K balina limiti
MEGA_WHALE_THRESHOLD = 1000000      # $1M mega balina limiti

# Takip Edilen Coinler (Binance Futures'te mevcut olanlar)
MONITORING_SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'SOL/USDT',
    'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'DOT/USDT', 'LTC/USDT',
    'TRX/USDT', 'ATOM/USDT', 'UNI/USDT', 'LINK/USDT', 'BCH/USDT',
    'NEAR/USDT', 'ICP/USDT', 'FET/USDT', 'SUI/USDT', 'APT/USDT'
]

# Monitoring Ayarları
SCAN_INTERVAL = 30                  # Tarama aralığı (saniye)
API_DELAY = 2                       # API çağrıları arası bekleme (saniye)
TRADES_LIMIT = 500                  # Her taramada kontrol edilecek işlem sayısı

# Alert Ayarları
ALERT_CONFIDENCE_THRESHOLD = 0.7    # Minimum güven skoru
ALERT_ACTIVITY_LEVELS = ['HIGH', 'EXTREME']  # Bildirim gönderilecek aktivite seviyeleri
ALERT_COOLDOWN = 300                # Aynı coin için alert arası minimum süre (saniye)

# Log Ayarları
LOG_LEVEL = "INFO"                  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "whale_positions.log"
MAX_LOG_SIZE = 10                   # MB
BACKUP_COUNT = 5

# Data Saklama Ayarları
DATA_RETENTION_HOURS = 24           # Veri saklama süresi (saat)
STATISTICS_UPDATE_INTERVAL = 300    # İstatistik güncelleme aralığı (saniye)

# Performance Ayarları
MAX_CONCURRENT_REQUESTS = 5         # Eşzamanlı maksimum API isteği
REQUEST_TIMEOUT = 30                # API timeout (saniye)
RETRY_ATTEMPTS = 3                  # Hata durumunda tekrar deneme sayısı

# Bildirim Mesaj Şablonları
ALERT_MESSAGE_TEMPLATE = """
{emoji} <b>BALİNA POZİSYON TESPİTİ</b>

🪙 <b>Coin:</b> {symbol}
{side_emoji} <b>Pozisyon:</b> {side}
💰 <b>Toplam Hacim:</b> ${volume:,.0f}
📊 <b>Güven:</b> {confidence:.1%}
🔥 <b>Aktivite:</b> {activity_level}
📈 <b>İşlem Sayısı:</b> {trade_count}

💎 <b>En Büyük İşlem:</b>
└ Değer: ${largest_trade_value:,.0f}
└ Tip: {largest_trade_type}
└ Zaman: {largest_trade_time}

⏰ <b>Tespit Zamanı:</b> {detection_time}
"""

DAILY_SUMMARY_TEMPLATE = """
{emoji} <b>GÜNLÜK BALİNA ÖZETİ</b>

📊 <b>Genel Sentiment:</b> {sentiment}
🪙 <b>Aktif Coin:</b> {active_coins}/{total_coins}

<b>🏆 TOP 5 BALİNA AKTİVİTESİ:</b>
{top_coins}

⏰ <b>Rapor Zamanı:</b> {report_time}
"""

# Debug Ayarları
DEBUG_MODE = False
VERBOSE_LOGGING = False
SAVE_RAW_DATA = False

# Test Ayarları (Sandbox mode için)
USE_TESTNET = False
TESTNET_API_KEY = ""
TESTNET_API_SECRET = "" 