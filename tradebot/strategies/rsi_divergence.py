import logging
from indicators.technical import calculate_rsi, calculate_macd

logger = logging.getLogger(__name__)

def calculate_rsi_divergence_score(df):
    """RSI Divergence puanlaması (25 puan)"""
    score = 0
    
    # RSI hesaplama
    rsi = calculate_rsi(df)
    
    # Güçlü RSI uyumsuzluğu tespiti (15 puan)
    price_trend = df['close'].iloc[-10:].mean() > df['close'].iloc[-20:-10].mean()
    rsi_trend = rsi.iloc[-10:].mean() > rsi.iloc[-20:-10].mean()
    
    divergence_type = None
    if price_trend != rsi_trend:  # Divergence var
        score += 15
        divergence_type = 'bullish' if not price_trend and rsi_trend else 'bearish'
    
    # MACD momentum teyidi (5 puan)
    macd, signal = calculate_macd(df)
    
    if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:  # MACD yukarı kesiş
        score += 5
    elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:  # MACD aşağı kesiş
        score += 5
    
    # RSI aşırı alım/satım bölgesi (5 puan)
    current_rsi = rsi.iloc[-1]
    if current_rsi < 30 or current_rsi > 70:
        score += 5
    
    logger.debug(f"RSI Divergence Score: {score}/25 - RSI: {current_rsi:.2f} - Divergence: {divergence_type}")
    return score, current_rsi, divergence_type