import logging
from config import STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT

logger = logging.getLogger(__name__)

def calculate_stop_loss(entry_price, position_type):
    """Calculate stop loss price"""
    if position_type == 'long':
        stop_loss = entry_price * (1 - STOP_LOSS_PERCENT / 100)
    else:  # short
        stop_loss = entry_price * (1 + STOP_LOSS_PERCENT / 100)
    return stop_loss

def calculate_take_profit(entry_price, position_type):
    """Calculate take profit price"""
    if position_type == 'long':
        take_profit = entry_price * (1 + TAKE_PROFIT_PERCENT / 100)
    else:  # short
        take_profit = entry_price * (1 - TAKE_PROFIT_PERCENT / 100)
    return take_profit

def check_position_pnl(symbol, position_type, entry_price, current_price, leverage=20):
    """Calculate position PnL"""
    try:
        if entry_price <= 0 or current_price <= 0:
            raise ValueError(f"Invalid prices: Entry={entry_price}, Current={current_price}")
        
        if position_type == "long":
            price_diff = current_price - entry_price
        elif position_type == "short":
            price_diff = entry_price - current_price
        else:
            raise ValueError(f"Invalid position type: {position_type}")
        
        raw_pnl = (price_diff / entry_price) * 100
        leveraged_pnl = raw_pnl * leverage
        
        logger.debug(f"[{symbol}] PnL Calculation: Type={position_type.upper()}, Entry={entry_price:.6f}, "
                    f"Current={current_price:.6f}, Raw PnL={raw_pnl:.2f}%, Leveraged={leveraged_pnl:.2f}%")
        
        return leveraged_pnl
        
    except Exception as e:
        logger.error(f"PnL calculation error for {symbol}: {e}")
        return 0