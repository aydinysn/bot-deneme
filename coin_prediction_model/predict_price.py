import sys
import ccxt
import joblib
import numpy as np
import pandas as pd
import logging
from datetime import datetime

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_latest_data(exchange, symbol, timeframe='1h', limit=100):
    """En son fiyat verilerini çek"""
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

def prepare_prediction_data(df, scaler):
    """Tahmin için veri hazırla"""
    df = df.dropna()
    
    features = ['open', 'high', 'low', 'close', 'volume', 'rsi', 'macd', 'signal', 
               'ma20', 'upper_band', 'lower_band', 'atr', 'momentum']
    
    X = df[features].values
    X_scaled = scaler.transform(X)
    
    return X_scaled[-60:].reshape(1, -1)  # Son 60 veriyi al ve reshape et

def load_models(symbol):
    """Kaydedilmiş modelleri yükle"""
    try:
        base_path = f"ml_models/saved_models/{symbol}"
        rf_model = joblib.load(f"{base_path}_rf.joblib")
        gb_model = joblib.load(f"{base_path}_gb.joblib")
        scaler = joblib.load(f"{base_path}_scaler.joblib")
        return rf_model, gb_model, scaler
    except Exception as e:
        logger.error(f"Model yükleme hatası: {e}")
        return None, None, None

def calculate_trend_strength(current_price, predictions):
    """Trend gücünü hesapla"""
    rf_pred, gb_pred = predictions
    avg_pred = (rf_pred + gb_pred) / 2
    
    # Yüzde değişim
    change_percent = ((avg_pred - current_price) / current_price) * 100
    
    # Tahminler arasındaki uyum
    agreement = 100 - (abs(rf_pred - gb_pred) / current_price * 100)
    
    return change_percent, agreement

def main():
    if len(sys.argv) != 2:
        print("Kullanım: python predict_price.py BTCUSDT")
        sys.exit(1)
    
    symbol = sys.argv[1]
    
    # Modelleri yükle
    rf_model, gb_model, scaler = load_models(symbol)
    if None in (rf_model, gb_model, scaler):
        logger.error("Modeller yüklenemedi!")
        return
    
    # Exchange bağlantısı
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        }
    })
    
    # En son verileri çek
    df = fetch_latest_data(exchange, symbol)
    if df is None:
        return
        
    # Teknik indikatörleri ekle
    df = add_technical_indicators(df)
    
    # Tahmin için veriyi hazırla
    X = prepare_prediction_data(df, scaler)
    
    # Tahminleri al
    rf_prediction = rf_model.predict(X)[0]
    gb_prediction = gb_model.predict(X)[0]
    
    # Mevcut fiyat
    current_price = df['close'].iloc[-1]
    
    # Trend analizi
    change_percent, agreement = calculate_trend_strength(current_price, (rf_prediction, gb_prediction))
    
    # Sonuçları yazdır
    logger.info(f"\n{'='*50}")
    logger.info(f"🪙 Coin: {symbol}")
    logger.info(f"📊 Mevcut Fiyat: ${current_price:.4f}")
    logger.info(f"\n📈 Tahminler:")
    logger.info(f"Random Forest: ${rf_prediction:.4f}")
    logger.info(f"Gradient Boosting: ${gb_prediction:.4f}")
    logger.info(f"Ortalama Tahmin: ${(rf_prediction + gb_prediction)/2:.4f}")
    logger.info(f"\n📊 Analiz:")
    logger.info(f"Beklenen Değişim: {change_percent:+.2f}%")
    logger.info(f"Model Uyumu: {agreement:.1f}%")
    logger.info(f"\n⏰ Tahmin Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info('='*50)

if __name__ == "__main__":
    main() 