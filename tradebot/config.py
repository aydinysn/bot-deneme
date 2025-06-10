# === config.py ===

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ================== CREDENTIALS ==================
# Binance API keys
API_KEY = os.getenv('BINANCE_API_KEY', '')
API_SECRET = os.getenv('BINANCE_API_SECRET', '')

# Telegram settings
TELEGRAM_TOKEN = '7653317241:AAH2t8-C4qBtzi9-zEnFF9mJ0csCFJ8iyVA'
TELEGRAM_CHAT_ID = '924928056'

# ================== TRADING SETTINGS ==================
# Basic trading parameters
TRADE_AMOUNT = 2.1  # Base amount per trade in USDT
LEVERAGE = 10      # Leverage multiplier
TIMEFRAME = '1h'  # Main timeframe for analysis
COIN_LIST_FILE = 'coins.json'  # File containing list of trading pairs

# ================== RISK MANAGEMENT ==================
# Position limits
MAX_POSITIONS = 5  # Maximum concurrent positions

# Stop Loss and Take Profit
STOP_LOSS_PERCENT = 5.0    # Stop loss percentage (kaldıraçlı)
TAKE_PROFIT_PERCENT = 15.0  # Take profit percentage (kaldıraçlı)

# ================== TRAILING STOP SETTINGS ==================
# Trailing stop configuration (kaldıraçlı PnL değerleri)
TRAILING_STOP_ACTIVATION = 8.0     # %10 kârda trailing stop aktif olur
TRAILING_STOP_DISTANCE = 8.0        # %5 mesafe (10'dan 5'e düşerse kapanır)
TRAILING_STOP_UPGRADE_LEVEL = 20.0  # %20 kârda trailing stop upgrade
TRAILING_STOP_UPGRADED_DISTANCE = 3.0  # Upgrade sonrası mesafe
TRAILING_STOP_STEP = 5.0 

# ================== ML PRICE PREDICTION SETTINGS ==================
# ML Model Configuration (Python 3.13 uyumlu)
ML_ENABLED = True                       # ML tahmin modelini kullan
ML_MODEL_TYPE = 'ensemble'              # 'rf', 'xgb', 'lgb', 'ensemble'
ML_SEQUENCE_LENGTH = 60                 # Girdi sekans uzunluğu (mum sayısı)

# ML Prediction Settings
ML_PREDICTION_STEPS = 3                 # Kaç adım öncesini tahmin et
ML_PREDICTION_WEIGHT = 0.3              # ML tahmininin sinyal skorundaki ağırlığı
ML_MIN_CONFIDENCE = 0.6                 # Minimum model güven skoru
ML_RETRAIN_INTERVAL_HOURS = 24          # Model yeniden eğitim aralığı (saat)

# ML Integration with Trading
ML_SIGNAL_THRESHOLD = 0.7               # Tahmin sinyali için minimum eşik
ML_TREND_CONFIRMATION = True            # Trend onayı için ML kullan
ML_PRICE_TARGET_WEIGHT = 0.4            # Take profit hesaplamada ML ağırlığı

# ================== LSTM PRICE PREDICTION SETTINGS ==================
# LSTM Model Configuration (TensorFlow gerekli)
LSTM_ENABLED = False                    # LSTM tahmin modelini kullan (TensorFlow gerekli)
LSTM_SEQUENCE_LENGTH = 60               # Girdi sekans uzunluğu (mum sayısı)
LSTM_UNITS = [50, 50, 30]              # Her LSTM katmanındaki nöron sayıları
LSTM_DROPOUT_RATE = 0.2                # Dropout oranı (overfitting önleme)
LSTM_LEARNING_RATE = 0.001             # Öğrenme oranı
LSTM_EPOCHS = 100                      # Maksimum eğitim epoch sayısı
LSTM_BATCH_SIZE = 32                   # Batch boyutu
LSTM_VALIDATION_SPLIT = 0.2            # Validation set oranı

# LSTM Prediction Settings
LSTM_PREDICTION_STEPS = 3              # Kaç adım öncesini tahmin et
LSTM_PREDICTION_WEIGHT = 0.3           # LSTM tahmininin sinyal skorundaki ağırlığı
LSTM_MIN_CONFIDENCE = 0.6              # Minimum model güven skoru
LSTM_RETRAIN_INTERVAL_HOURS = 24       # Model yeniden eğitim aralığı (saat)

# LSTM Integration with Trading
LSTM_SIGNAL_THRESHOLD = 0.7            # Tahmin sinyali için minimum eşik
LSTM_TREND_CONFIRMATION = True         # Trend onayı için LSTM kullan
LSTM_PRICE_TARGET_WEIGHT = 0.4         # Take profit hesaplamada LSTM ağırlığı

# ================== SIGNAL THRESHOLDS ==================
# Signal strength thresholds (0-100 scale)
WEAK_SIGNAL_THRESHOLD = 65.0    # Minimum score to open position
MEDIUM_SIGNAL_THRESHOLD = 75.0  # Medium strength signal
STRONG_SIGNAL_THRESHOLD = 85.0  # Strong signal threshold

# Position sizing based on signal strength
POSITION_SIZE_MAPPING = {
    'WEAK': 0.8,    # 60% of base amount
    'MEDIUM': 1.0,  # 80% of base amount  
    'STRONG': 1.2   # 100% of base amount
}

# ================== TECHNICAL ANALYSIS SETTINGS ==================
# RSI settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
RSI_DIVERGENCE_LOOKBACK = 10  # Candles to look back for divergence

# Bollinger Bands settings
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2.0
BOLLINGER_SQUEEZE_THRESHOLD = 0.002  # Minimum squeeze percentage

# ATR settings
ATR_PERIOD = 14
ATR_MULTIPLIER = 1.5  # For stop loss calculation

# Market structure settings
MARKET_STRUCTURE_LOOKBACK = 20  # Candles to analyze market structure
TREND_STRENGTH_THRESHOLD = 0.6  # Minimum trend strength to trade

# ================== MULTI-TIMEFRAME SETTINGS ==================
# Additional timeframes for analysis
MULTI_TIMEFRAMES = ['5m', '15m', '1h', '4h']
MTF_WEIGHT_MAPPING = {
    '5m': 0.15,
    '15m': 0.35,  # Main timeframe gets highest weight
    '1h': 0.3,
    '4h': 0.2
}

# ================== FILTERS AND PENALTIES ==================
# Volume filter
VOLUME_MA_PERIOD = 20
MIN_VOLUME_RATIO = 1.0  # Current volume must be at least 1x the average

# Volatility filter
MIN_ATR_PERCENT = 0.5   # Minimum volatility to trade
MAX_ATR_PERCENT = 5.0   # Maximum volatility to trade

# Trend alignment penalties
CONTRA_TREND_PENALTY = 0.5  # 50% penalty for trading against main trend
DIVERGENCE_CONFLICT_PENALTY = 0.3  # 30% penalty for conflicting signals

# ================== SYSTEM SETTINGS ==================
# Logging and debugging
LOG_LEVEL = 'INFO'
LOG_FILE_PATH = 'logs/'
MAX_LOG_FILES = 7  # Keep logs for 7 days
DEBUG_MODE = False

# Time settings
SCAN_INTERVAL = 30  # Seconds between full market scans
POSITION_CHECK_INTERVAL = 10  # Seconds between position checks
COOLDOWN_PERIOD = 300  # Seconds to wait before re-entering same coin

# API rate limiting
API_RATE_LIMIT = 1200  # Max requests per minute
REQUEST_DELAY = 0.1    # Seconds between API calls

# ================== PERFORMANCE TRACKING ==================
# Statistics tracking
TRACK_PERFORMANCE = True
STATS_FILE = 'trading_stats.json'
DAILY_REPORT_TIME = '00:00'  # Time to generate daily report

# ================== NOTIFICATION SETTINGS ==================
# Telegram notification levels
NOTIFY_SIGNALS = False  # Notify on all signals
NOTIFY_TRADES = True   # Notify on trade executions
NOTIFY_ERRORS = True   # Notify on errors
NOTIFY_DAILY_REPORT = True  # Send daily performance report
NOTIFY_ML_PREDICTIONS = True  # ML tahmin bildirimleri
NOTIFY_LSTM_PREDICTIONS = True  # LSTM tahmin bildirimleri

# ================== ADVANCED SETTINGS ==================
# Order execution
ORDER_TYPE = 'MARKET'  # MARKET or LIMIT
LIMIT_ORDER_OFFSET = 0.05  # % offset for limit orders
MAX_SLIPPAGE = 0.1    # Maximum allowed slippage

# Exchange specific settings
EXCHANGE_FEES = 0.1   # Trading fees percentage
MIN_NOTIONAL = 20     # Minimum order value in USDT

# Safety checks
ENABLE_SAFETY_CHECKS = True
MAX_DAILY_LOSS = 50   # Maximum daily loss in USDT
MAX_DRAWDOWN = 20     # Maximum drawdown percentage