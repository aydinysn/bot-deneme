import logging
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)


def load_coins_from_json(filename='coins.json'):
    """Load coin list from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    coins = data
                elif isinstance(data, dict) and 'coins' in data:
                    coins = data['coins']
                else:
                    logger.error("Invalid JSON format")
                    return None
            logger.info(f"Loaded {len(coins)} coins from {filename}")
            return coins
        else:
            logger.error(f"Coin file not found: {filename}")
            return None
    except Exception as e:
        logger.error(f"Error loading coins from JSON: {e}")
        return None

def save_coins_to_json(coins, filename='coins.json'):
    """Coin listesini JSON dosyasına kaydeder"""
    try:
        data = {
            "coins": coins,
            "last_updated": datetime.now().isoformat()
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Saved {len(coins)} coins to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving coins to JSON: {e}")
        return False