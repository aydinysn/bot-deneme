"""
Whale Tracker Configuration
Whale tracker için tüm ayarlar
"""

# ================== WHALE TRACKER SETTINGS ==================

# Whale tanım kriterleri
WHALE_THRESHOLD_BTC = 100        # 100+ BTC transferi whale sayılır
WHALE_THRESHOLD_ETH = 1000       # 1000+ ETH transferi whale sayılır
WHALE_THRESHOLD_USDT = 1000000   # 1M+ USDT transferi whale sayılır

# Diğer coinler için USD değeri
WHALE_THRESHOLD_USD = 1000000    # 1M+ USD değeri whale sayılır

# Exchange wallet'ları (büyük transfer = satış riski)
MAJOR_EXCHANGES = [
    "binance",
    "coinbase", 
    "kraken",
    "okx",
    "bybit",
    "bitfinex",
    "huobi",
    "kucoin"
]

# API Ayarları
WHALE_ALERT_API_KEY = "your_whale_alert_api_key"  # WhaleAlert.io API key
ETHERSCAN_API_KEY = "your_etherscan_api_key"      # Etherscan API key
BSCSCAN_API_KEY = "your_bscscan_api_key"          # BSCScan API key

# ================== TELEGRAM BOT SETTINGS ==================

# Bot Token ve Chat ID'yi buraya girin
# ADIM 1: @BotFather'da bot oluşturun ve token'ı buraya yapıştırın
TELEGRAM_BOT_TOKEN = "7807140773:AAFSLyU9e6Dfw7XPP5r2GwmdmdHndOSTong"    # ÖRN: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456"

# ADIM 2: Chat ID'nizi bulun ve buraya girin 
TELEGRAM_CHAT_ID = "924928056"                 # ÖRN: "123456789" veya grup için "-123456789"

# Telegram bildirimlerini aktif et
TELEGRAM_ENABLED = True                           # False yaparsanız Telegram bildirimleri kapanır

# Hangi bildirimlerin gönderileceğini seçin
TELEGRAM_SEND_WHALE_MOVEMENTS = True              # Whale hareketlerini gönder
TELEGRAM_SEND_SIGNALS = True                      # Trading sinyallerini gönder
TELEGRAM_SEND_PATTERNS = True                     # Pattern tespitlerini gönder
TELEGRAM_SEND_ALERTS = True                       # Market alertlerini gönder

# Mesaj ayarları
TELEGRAM_PARSE_MODE = "Markdown"                  # "Markdown" veya "HTML"
TELEGRAM_DISABLE_PREVIEW = True                   # Link preview'ları kapat
TELEGRAM_SEND_ONLY_STRONG = False                 # Sadece güçlü sinyaller (True/False)

# Monitoring ayarları
CHECK_INTERVAL_SECONDS = 60      # Her 60 saniyede bir kontrol
MAX_LOOKBACK_HOURS = 24          # Son 24 saati kontrol et
MIN_SIGNAL_INTERVAL = 300        # Aynı coin için min 5 dk ara

# Signal güç seviyeleri
SIGNAL_STRENGTH = {
    'MINOR': 1000000,     # 1M USD
    'MODERATE': 5000000,  # 5M USD  
    'MAJOR': 10000000,    # 10M USD
    'EXTREME': 50000000   # 50M USD
}

# Takip edilecek coinler
TRACKED_COINS = [
    'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE', 'DOT',
    'MATIC', 'LTC', 'SHIB', 'TRX', 'AVAX', 'LINK', 'ATOM',
    'XLM', 'BCH', 'NEAR', 'FLOW', 'SAND', 'MANA', 'CHZ'
]

# Notification ayarları
ENABLE_WHALE_NOTIFICATIONS = True
NOTIFY_MINOR_WHALES = False      # Sadece büyük whale'ler için bildirim
NOTIFY_EXCHANGE_FLOWS = True     # Exchange'e gelen/giden transferler
NOTIFY_UNKNOWN_WALLETS = True    # Bilinmeyen cüzdan hareketleri

# Trading signal ayarları
GENERATE_SIGNALS = True
SIGNAL_CONFIDENCE_THRESHOLD = 0.6  # Minimum güven skoru
SIGNAL_DECAY_HOURS = 4             # Signal 4 saat sonra geçersiz
AUTO_TRADING_ENABLED = False       # Otomatik trading (dikkatli!)

# Cache ayarları
CACHE_WHALE_DATA = True
CACHE_DURATION_MINUTES = 30
MAX_CACHE_SIZE = 1000

# Rate limiting
API_RATE_LIMIT_PER_MINUTE = 50
REQUESTS_PER_SECOND = 1

# Logging
LOG_WHALE_MOVEMENTS = True
LOG_FILE_PATH = "whale_tracker/logs/"
MAX_LOG_FILES = 7  # 7 günlük log tut 