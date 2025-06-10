# === utils/position_sizing.py ===
import logging
from config import (
    POSITION_SIZE_MAPPING,
    STRONG_SIGNAL_THRESHOLD,
    MEDIUM_SIGNAL_THRESHOLD,
    WEAK_SIGNAL_THRESHOLD
)

def determine_position_size(signal_score):
    """Determine position size based on signal strength"""
    if signal_score >= STRONG_SIGNAL_THRESHOLD:
        return POSITION_SIZE_MAPPING['STRONG']
    elif signal_score >= MEDIUM_SIGNAL_THRESHOLD:
        return POSITION_SIZE_MAPPING['MEDIUM']
    elif signal_score >= WEAK_SIGNAL_THRESHOLD:
        return POSITION_SIZE_MAPPING['WEAK']
    else:
        return 0  # No position for weak signals

def calculate_position_amount(base_amount, signal_score):
    """Calculate actual position amount based on signal strength"""
    size_multiplier = determine_position_size(signal_score)
    return base_amount * size_multiplier