"""
Whale Tracker Module - Büyük Cüzdan Takip Sistemi

Bu modül, büyük kripto cüzdan hareketlerini takip eder ve
trading sinyalleri üretir.
"""

from .whale_tracker import WhaleTracker
from .whale_api import WhaleAPI
from .whale_analyzer import WhaleAnalyzer
from .whale_signals import WhaleSignalGenerator
from .whale_notifications import WhaleNotifier

__all__ = [
    'WhaleTracker',
    'WhaleAPI', 
    'WhaleAnalyzer',
    'WhaleSignalGenerator',
    'WhaleNotifier'
]

__version__ = "1.0.0" 