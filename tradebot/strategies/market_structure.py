import logging
from indicators.technical import calculate_atr

logger = logging.getLogger(__name__)

def calculate_market_structure_score(df):
    """Market yapısı ve hacim puanlaması (30 puan)"""
    score = 0
    
    # Higher High/Lower Low trend tespiti (15 puan)
    highs = df['high'].rolling(window=20).max()
    lows = df['low'].rolling(window=20).min()
    
    trend_direction = None
    if df['high'].iloc[-1] > highs.iloc[-2]:  # Higher High
        trend_direction = 'long'
        score += 15
    elif df['low'].iloc[-1] < lows.iloc[-2]:  # Lower Low
        trend_direction = 'short'
        score += 15
    
    # Hacim artışı teyidi (10 puan)
    avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
    current_volume = df['volume'].iloc[-1]
    
    if current_volume > avg_volume * 1.5:
        score += 10
    
    # Destek/direnç seviyesine yakınlık (5 puan)
    recent_highs = df['high'].tail(50).max()
    recent_lows = df['low'].tail(50).min()
    current_price = df['close'].iloc[-1]
    
    if abs(current_price - recent_lows) / current_price < 0.02:  # %2 yakınlıkta
        score += 5
    elif abs(current_price - recent_highs) / current_price < 0.02:
        score += 5
    
    logger.debug(f"Market Structure Score: {score}/30 - Trend: {trend_direction}")
    return score, trend_direction