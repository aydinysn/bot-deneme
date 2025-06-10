import logging
from indicators.technical import calculate_bollinger_bands
from indicators.volume_profile import find_poc_level

logger = logging.getLogger(__name__)

def calculate_bollinger_score(df):
    """Bollinger Band Sıkışma puanlaması (20 puan)"""
    score = 0
    
    # Bollinger Bands hesaplama
    upper_band, middle_band, lower_band = calculate_bollinger_bands(df)
    
    # Band sıkışması tespiti (10 puan)
    current_width = (upper_band.iloc[-1] - lower_band.iloc[-1]) / middle_band.iloc[-1]
    avg_width = ((upper_band - lower_band) / middle_band).rolling(window=50).mean().iloc[-1]
    
    squeeze_detected = False
    if current_width < avg_width * 0.7:  # %30 daha dar
        score += 10
        squeeze_detected = True
    
    # Fiyatın banda dokunması (5 puan)
    current_price = df['close'].iloc[-1]
    band_touch = None
    
    if abs(current_price - lower_band.iloc[-1]) < current_price * 0.001:  # Alt banda değiyor
        score += 5
        band_touch = 'lower'
    elif abs(current_price - upper_band.iloc[-1]) < current_price * 0.001:  # Üst banda değiyor
        score += 5
        band_touch = 'upper'
    
    # Hacim profili POC seviyesi teyidi (5 puan)
    poc_price = find_poc_level(df)
    
    if abs(current_price - poc_price) / current_price < 0.01:  # POC'a %1 yakın
        score += 5
    
    logger.debug(f"Bollinger Bands Score: {score}/20 - Squeeze: {squeeze_detected} - Touch: {band_touch}")
    return score, squeeze_detected, band_touch