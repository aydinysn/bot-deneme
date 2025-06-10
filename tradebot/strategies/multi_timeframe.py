import logging
import pandas as pd

logger = logging.getLogger(__name__)

def calculate_multi_timeframe_score(exchange, symbol):
    """Çoklu Zaman Dilimi Teyit puanlaması (25 puan)"""
    score = 0
    
    trend_alignment = {}
    
    # 15 dakikalık trend uyumu (5 puan)
    df_15m = pd.DataFrame(exchange.fetch_ohlcv(symbol, timeframe='15m', limit=50),
                          columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    trend_15m = df_15m['close'].iloc[-1] > df_15m['close'].rolling(window=20).mean().iloc[-1]
    trend_alignment['15m'] = trend_15m
    if trend_15m:
        score += 5
    
    # 1 saatlik trend uyumu (10 puan)
    df_1h = pd.DataFrame(exchange.fetch_ohlcv(symbol, timeframe='1h', limit=50),
                         columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    trend_1h = df_1h['close'].iloc[-1] > df_1h['close'].rolling(window=20).mean().iloc[-1]
    trend_alignment['1h'] = trend_1h
    if trend_1h:
        score += 10
    
    # 4 saatlik trend uyumu (10 puan)
    df_4h = pd.DataFrame(exchange.fetch_ohlcv(symbol, timeframe='4h', limit=50),
                         columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    trend_4h = df_4h['close'].iloc[-1] > df_4h['close'].rolling(window=20).mean().iloc[-1]
    trend_alignment['4h'] = trend_4h
    if trend_4h:
        score += 10
    
    # Tüm zaman dilimleri aynı yönde mi?
    all_aligned = all(trend_alignment.values()) or not any(trend_alignment.values())
    
    logger.debug(f"Multi-Timeframe Score: {score}/25 - Alignment: {trend_alignment} - Fully Aligned: {all_aligned}")
    return score, trend_alignment, all_aligned