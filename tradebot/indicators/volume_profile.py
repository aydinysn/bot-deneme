import numpy as np
import pandas as pd

def calculate_volume_profile(df, bins=50):
    """Calculate volume profile for given data"""
    price_range = np.linspace(df['low'].min(), df['high'].max(), bins)
    volume_profile = []
    
    for i in range(len(price_range) - 1):
        mask = (df['low'] <= price_range[i+1]) & (df['high'] >= price_range[i])
        volume_in_range = df.loc[mask, 'volume'].sum()
        volume_profile.append({
            'price': (price_range[i] + price_range[i+1]) / 2,
            'volume': volume_in_range
        })
    
    return pd.DataFrame(volume_profile)

def find_poc_level(df, lookback=50):
    """Find Point of Control (POC) level"""
    recent_data = df.tail(lookback)
    volume_profile = calculate_volume_profile(recent_data)
    poc_index = volume_profile['volume'].idxmax()
    poc_price = volume_profile.loc[poc_index, 'price']
    return poc_price
