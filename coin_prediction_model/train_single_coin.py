import sys
import ccxt
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import logging
import os
from datetime import datetime, timedelta

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_historical_data(exchange, symbol, timeframe='1h', limit=1000):
    """Geçmiş fiyat verilerini çek"""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        logger.error(f"Veri çekme hatası: {e}")
        return None

def add_technical_indicators(df):
    """Teknik indikatörleri ekle"""
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['20std'] = df['close'].rolling(window=20).std()
    df['upper_band'] = df['ma20'] + (df['20std'] * 2)
    df['lower_band'] = df['ma20'] - (df['20std'] * 2)
    
    # ATR
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['atr'] = true_range.rolling(14).mean()
    
    # Momentum
    df['momentum'] = df['close'] - df['close'].shift(4)
    
    return df

def prepare_data(df, sequence_length=60):
    """Model için veri hazırla"""
    df = df.dropna()
    
    # Özellikler ve hedef
    features = ['open', 'high', 'low', 'close', 'volume', 'rsi', 'macd', 'signal', 
                'ma20', 'upper_band', 'lower_band', 'atr', 'momentum']
    
    X = df[features].values
    y = df['close'].shift(-1).values  # Bir sonraki kapanış fiyatı
    
    # NaN değerleri kaldır
    X = X[:-1]
    y = y[:-1]
    
    # Veriyi normalize et
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Sequence oluştur
    X_seq = []
    y_seq = []
    
    for i in range(len(X_scaled) - sequence_length):
        X_seq.append(X_scaled[i:(i + sequence_length)])
        y_seq.append(y[i + sequence_length])
    
    return np.array(X_seq), np.array(y_seq), scaler

def train_model(X, y):
    """Ensemble model eğit"""
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Random Forest
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train.reshape(X_train.shape[0], -1), y_train)
    
    # Gradient Boosting
    gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    gb_model.fit(X_train.reshape(X_train.shape[0], -1), y_train)
    
    # Test performansı
    rf_score = rf_model.score(X_test.reshape(X_test.shape[0], -1), y_test)
    gb_score = gb_model.score(X_test.reshape(X_test.shape[0], -1), y_test)
    
    logger.info(f"Random Forest R2 Score: {rf_score:.4f}")
    logger.info(f"Gradient Boosting R2 Score: {gb_score:.4f}")
    
    return rf_model, gb_model

def main():
    if len(sys.argv) != 2:
        print("Kullanım: python train_single_coin.py BTCUSDT")
        sys.exit(1)
    
    symbol = sys.argv[1]
    
    # Model kayıt dizini oluştur
    os.makedirs('ml_models/saved_models', exist_ok=True)
    
    # Exchange bağlantısı
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        }
    })
    
    # Veri çek
    logger.info(f"{symbol} için veri çekiliyor...")
    df = fetch_historical_data(exchange, symbol)
    if df is None:
        logger.error("Veri çekilemedi!")
        return
    
    # İndikatörleri ekle
    logger.info("Teknik indikatörler ekleniyor...")
    df = add_technical_indicators(df)
    
    # Veriyi hazırla
    logger.info("Veri hazırlanıyor...")
    X, y, scaler = prepare_data(df)
    
    # Modeli eğit
    logger.info("Model eğitiliyor...")
    rf_model, gb_model = train_model(X, y)
    
    # Modelleri kaydet
    model_path = f"ml_models/saved_models/{symbol.replace('/', '')}"
    joblib.dump(rf_model, f"{model_path}_rf.joblib")
    joblib.dump(gb_model, f"{model_path}_gb.joblib")
    joblib.dump(scaler, f"{model_path}_scaler.joblib")
    
    logger.info(f"Modeller kaydedildi: {model_path}")

if __name__ == "__main__":
    main() 