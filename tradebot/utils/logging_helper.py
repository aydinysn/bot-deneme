# === utils/logging_helper.py ===
import logging
import os
from datetime import datetime

def setup_logging(debug_mode=False):
    """Setup logging configuration with logs folder"""
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    
    # Create log filename with date
    log_filename = f"{datetime.now().strftime('%Y-%m-%d')}.txt"
    log_filepath = os.path.join(logs_dir, log_filename)
    
    logging.basicConfig(
        level=logging.DEBUG if debug_mode else logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_filepath, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Disable debug logs for some libraries
    logging.getLogger('ccxt').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging started - Log file: {log_filepath}")

def log_trade_action(action, symbol, details):
    """Log trade actions with consistent formatting"""
    logger = logging.getLogger(__name__)
    
    log_message = f"[{action}] {symbol} - "
    log_message += " | ".join([f"{k}: {v}" for k, v in details.items()])
    
    logger.info(log_message)