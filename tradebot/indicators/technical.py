import pandas as pd
import numpy as np

def calculate_ema(df, short=9, long=21):
    """Calculate EMA indicators"""
    df['short_ema'] = df['close'].ewm(span=short, adjust=False).mean()
    df['long_ema'] = df['close'].ewm(span=long, adjust=False).mean()
    return df

def calculate_rsi(df, period=14):
    """Calculate RSI indicator"""
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_atr(df, period=14):
    """Calculate Average True Range (ATR)"""
    df['previous_close'] = df['close'].shift(1)
    df['tr'] = df[['high', 'low', 'previous_close']].apply(
        lambda row: max(
            row['high'] - row['low'],
            abs(row['high'] - row['previous_close']),
            abs(row['low'] - row['previous_close'])
        ), axis=1
    )
    df['atr'] = df['tr'].rolling(window=period).mean()
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    """Calculate MACD indicator"""
    exp1 = df['close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def calculate_bollinger_bands(df, window=20, std_dev=2):
    """Calculate Bollinger Bands"""
    middle_band = df['close'].rolling(window=window).mean()
    std = df['close'].rolling(window=window).std()
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    return upper_band, middle_band, lower_band
