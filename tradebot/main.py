# === main.py ===
import sys
import locale
import time
import ccxt
import pandas as pd
import logging
from datetime import datetime
import traceback

if sys.platform.startswith('win'):
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
        except:
            pass

# Local imports
from config import *
from indicators.technical import calculate_atr
from strategies import (
    calculate_market_structure_score,
    calculate_rsi_divergence_score,
    calculate_bollinger_score,
    calculate_multi_timeframe_score
)
from utils import (
    setup_logging,
    log_trade_action,
    check_position_pnl,
    determine_position_size,
    calculate_position_amount
)
from utils.coin_manager import load_coins_from_json

# Setup logging
setup_logging(DEBUG_MODE)
logger = logging.getLogger(__name__)

# Global variables
exchange = None  # Global exchange değişkeni
positions = {}
trailing_stops = {}
recently_closed = {}
ACCOUNT_BALANCE = 0
initial_daily_balance = 0.0  # Günlük başlangıç bakiyesi
current_balance = 0.0  # Güncel bakiye
last_reset_date = None  # Son sıfırlama tarihi
daily_limit_notified = False  # Günlük limit bildirim flag'i

def set_leverage_for_all_coins(coin_list):
    """Set leverage for all coins at bot startup"""
    logger.info(f"Setting leverage to {LEVERAGE}x for all coins...")
    
    successful = 0
    failed = 0
    
    for coin in coin_list:
        try:
            symbol = coin  # coin is already in format like "BTC/USDT"
            # Set leverage for this symbol
            exchange.set_leverage(LEVERAGE, symbol)
            successful += 1
            logger.debug(f"Leverage set to {LEVERAGE}x for {symbol}")
        except Exception as e:
            failed += 1
            logger.warning(f"Failed to set leverage for {symbol}: {e}")
    
    logger.info(f"Leverage setting completed: {successful} successful, {failed} failed")
    return successful, failed

def initialize_exchange():
    """Initialize exchange connection"""
    global exchange
    
    try:
        exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'defaultMarket': 'future',
                'defaultMarginMode': 'isolated',
                'recvWindow': 60000,  # Daha uzun timeout
                'adjustForTimeDifference': True,  # Otomatik zaman ayarı
            }
        })
        exchange.load_markets()
        
        # Test için balance çek
        test_balance = exchange.fetch_balance()
        logger.info("API connection successful")
        
        return exchange
    except Exception as e:
        logger.error(f"Exchange initialization error: {e}")
        sys.exit(1)
        # Position mode kontrolü
        check_position_mode()
        
        return exchange
    except Exception as e:
        logger.error(f"Exchange initialization error: {str(e)[:200]}")
        sys.exit(1)

def send_telegram(message):
    """Send message to Telegram"""
    try:
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            logger.error(f"Telegram send error: {response.text}")
    except Exception as e:
        logger.error(f"Telegram error: {str(e)}")

def check_position_mode():
    """Check current position mode on Binance Futures"""
    try:
        response = exchange.fapiPrivateGetPositionSideDual()
        dual_side_position = response['dualSidePosition']
        
        if dual_side_position:
            logger.info("Current position mode: HEDGE MODE (dual side position)")
        else:
            logger.info("Current position mode: ONE-WAY MODE")
            
        return dual_side_position
    except Exception as e:
        logger.error(f"Error checking position mode: {e}")
        return None
def load_balance():
    """Load account balance"""
    global ACCOUNT_BALANCE
    try:
        # Balance bilgisini çek
        balance_info = exchange.fetch_balance()
        
        # Debug için balance_info'yu logla
        logger.debug(f"Balance info structure: {balance_info}")
        logger.debug(f"Available keys: {list(balance_info.keys())}")
        
        total_balance = 0
        avail_balance = 0
        
        # Binance futures balance formatı
        if 'info' in balance_info:
            if 'totalWalletBalance' in balance_info['info']:
                total_balance = float(balance_info['info']['totalWalletBalance'])
                avail_balance = float(balance_info['info']['availableBalance'])
            elif 'assets' in balance_info['info']:
                for asset in balance_info['info']['assets']:
                    if asset['asset'] == 'USDT':
                        total_balance = float(asset['walletBalance'])
                        avail_balance = float(asset['availableBalance'])
                        break
        
        ACCOUNT_BALANCE = total_balance
        
        logger.info(f"Balance - Total: ${total_balance:.2f} | Available: ${avail_balance:.2f}")
        
        # Balance kontrolü düzelt
        return True
            
    except Exception as e:
        logger.error(f"Failed to load balance: {e}")
        logger.error(f"Balance info: {balance_info if 'balance_info' in locals() else 'Not available'}")
        import traceback
        logger.error(traceback.format_exc())
        return False
def check_position_value(symbol, amount, price):
    """Check if position value is within available margin"""
    try:
        position_value = amount * price
        required_margin = position_value / LEVERAGE
        
        logger.info(f"Position Check - Value: ${position_value:.2f} | Required Margin: ${required_margin:.2f}")
        
        available_balance = load_balance()
        if required_margin > available_balance:
            logger.warning(f"Insufficient margin! Required: ${required_margin:.2f} | Available: ${available_balance:.2f}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error checking position value: {e}")
        return False

def get_ohlcv_data(symbol, timeframe='15m', limit=100):
    """Fetch OHLCV data for a symbol"""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if not ohlcv or len(ohlcv) < limit:
            logger.warning(f"Incomplete OHLCV data for {symbol}: got {len(ohlcv)} candles, expected {limit}")
            if not ohlcv:
                return None
                
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Add technical indicators
        df = calculate_atr(df)
        
        return df
    except Exception as e:
        logger.error(f"OHLCV data fetch error ({symbol}): {str(e)}")
        return None

def calculate_total_signal_score(df, symbol):
    """Calculate total signal score based on all strategies"""
    try:
        # 1. Market Structure Score
        market_score, trend_direction = calculate_market_structure_score(df)
        
        # 2. RSI Divergence Score  
        rsi_score, current_rsi, divergence_type = calculate_rsi_divergence_score(df)
        
        # 3. Bollinger Bands Score
        bollinger_score, squeeze_detected, band_touch = calculate_bollinger_score(df)
        
        # 4. Multi-Timeframe Score
        mtf_score, trend_alignment, all_aligned = calculate_multi_timeframe_score(exchange, symbol)
        
        # Calculate total score
        total_score = market_score + rsi_score + bollinger_score + mtf_score
        
        # Apply filters and penalties
        penalty = 0
        
        # Contradiction penalty
        if divergence_type == 'bearish' and trend_direction == 'long':
            penalty += 0.3
        elif divergence_type == 'bullish' and trend_direction == 'short':
            penalty += 0.3
            
        # Trend filter (200 MA)
        ma_200 = df['close'].rolling(window=200).mean().iloc[-1] if len(df) >= 200 else df['close'].mean()
        current_price = df['close'].iloc[-1]
        
        if (trend_direction == 'long' and current_price < ma_200) or \
           (trend_direction == 'short' and current_price > ma_200):
            penalty += 0.5
            
        # Volatility filter
        atr = df['atr'].iloc[-1]
        atr_percent = (atr / current_price) * 100
        
        if atr_percent < 0.5:  # Very low volatility
            penalty += 0.2
            
        # Apply penalty
        final_score = total_score * (1 - penalty)
        
        # Only log if signal is strong enough to potentially trade
        if final_score >= WEAK_SIGNAL_THRESHOLD:
            logger.info(f"Signal Alert: {symbol} - Score: {final_score:.1f}/100 - Trend: {trend_direction}")
        
        return final_score, trend_direction
        
    except Exception as e:
        logger.error(f"Error calculating signal score for {symbol}: {e}")
        logger.error(traceback.format_exc())
        return 0, None

def get_signal_strength(score):
    """Get signal strength description"""
    if score >= STRONG_SIGNAL_THRESHOLD:
        return "STRONG"
    elif score >= MEDIUM_SIGNAL_THRESHOLD:
        return "MEDIUM"
    elif score >= WEAK_SIGNAL_THRESHOLD:
        return "WEAK"
    else:
        return "NO SIGNAL"
def calculate_dynamic_risk_levels(symbol, signal_score, current_price, atr):
    """Calculate dynamic stop loss and take profit levels based on signal strength and ATR"""
    try:
        # ATR bazlı dinamik risk yönetimi
        if signal_score >= 90:
            sl_multiplier = 10
            tp_multiplier = 30
        elif signal_score >= 70:
            sl_multiplier = 15
            tp_multiplier = 25
        else:  # 50-69 puan
            sl_multiplier = 20
            tp_multiplier = 15
        
        # Stop loss ve take profit seviyeleri
        stop_loss_distance = atr * sl_multiplier
        take_profit_distance = atr * tp_multiplier
        
        # Yüzde olarak hesapla
        stop_loss_percent = (stop_loss_distance / current_price) * 100
        take_profit_percent = (take_profit_distance / current_price) * 100
        
        logger.info(f"Dynamic Risk Levels for {symbol} (Score: {signal_score:.1f})")
        logger.info(f"ATR: {atr:.6f} | Current Price: {current_price:.6f}")
        logger.info(f"Stop Loss: {stop_loss_percent:.2f}% | Take Profit: {take_profit_percent:.2f}%")
        
        return stop_loss_percent, take_profit_percent
        
    except Exception as e:
        logger.error(f"Error calculating dynamic risk levels: {e}")
        # Fallback to default values
        return STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT   

def place_order(symbol, order_type, signal_score):
    """Place order with position sizing based on signal strength"""
    try:
        # Check if position already exists
        if symbol in positions:
            logger.info(f"Position already exists for {symbol}, skipping order")
            return False
        
        # Get trading amount based on signal strength
        position_amount = calculate_position_amount(TRADE_AMOUNT, signal_score)
        
        # Minimum position value check
        MIN_POSITION_VALUE = 20  # Binance minimum
       
        
        # Use global balance info instead of fetching again
        total_balance = ACCOUNT_BALANCE
        available_balance = ACCOUNT_BALANCE
        
        logger.info(f"Balance - Total: ${total_balance:.2f} | Available: ${available_balance:.2f}")
        notional_value = position_amount * LEVERAGE
        if notional_value < MIN_POSITION_VALUE:
            # Minimum notional değere ulaşmıyor
            required_margin = MIN_POSITION_VALUE / LEVERAGE
            logger.info(f"Position notional too small: ${position_amount:.2f} * {LEVERAGE}x = ${notional_value:.2f} < ${MIN_POSITION_VALUE}")
            
            # If balance is sufficient, increase to minimum
            if available_balance >= required_margin:
                position_amount = required_margin
                logger.info(f"Increased position amount to minimum: ${position_amount:.2f}")
            else:
                logger.warning(f"Insufficient balance even for minimum position. Required: ${required_margin:.2f}, Available: ${available_balance:.2f}")
                return False
        # Balance check
        if position_amount > available_balance:
            logger.warning(f"Insufficient balance for {symbol}. Required: ${position_amount:.2f}, Available: ${available_balance:.2f}")
            return False
            
        # Get current price
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Get OHLCV data for ATR
        df = get_ohlcv_data(symbol)
        if df is None or 'atr' not in df:
            logger.error(f"Cannot get ATR for {symbol}")
            return False
            
        current_atr = df['atr'].iloc[-1]
        
        # Calculate dynamic risk levels
        stop_loss_percent, take_profit_percent = calculate_dynamic_risk_levels(
            symbol, signal_score, current_price, current_atr
        )
        
        # Calculate quantity
        raw_amount = (position_amount * LEVERAGE) / current_price
        market = exchange.market(symbol)
        
        # Apply LOT_SIZE filter
        amount_filter = next((f for f in market['info']['filters'] if f['filterType'] == 'LOT_SIZE'), None)
        if amount_filter:
            min_qty = float(amount_filter['minQty'])
            step_size = float(amount_filter['stepSize'])
            precision = len(str(step_size).split('.')[-1].rstrip('0')) if '.' in str(step_size) else 0
            amount = round(max(min_qty, round(raw_amount / step_size) * step_size), precision)
        else:
            amount = round(raw_amount, 3)
            
        # Check final notional value
        notional = amount * current_price
        if notional < MIN_POSITION_VALUE:
            logger.warning(f"Order value still too low after adjustments! Notional: ${notional:.2f} < ${MIN_POSITION_VALUE} minimum")
            return False
            
        # Place order
        side = 'BUY' if order_type == 'long' else 'SELL'
        
        # Hedge mode parameters
        params = {}
        position_side = 'LONG' if order_type == 'long' else 'SHORT'
        params['positionSide'] = position_side
        
        order = exchange.create_market_order(
            symbol=symbol,
            side=side,
            amount=amount,
            params=params
        )
        
        # Save position info with dynamic risk levels
        positions[symbol] = {
            'type': order_type,
            'entry_price': current_price,
            'amount': amount,
            'signal_score': signal_score,
            'open_time': datetime.now().isoformat(),
            'stop_loss_percent': stop_loss_percent,
            'take_profit_percent': take_profit_percent,
            'atr': current_atr
        }
        
        # Setup trailing stop
        setup_trailing_stop(symbol, order_type, current_price)
        
        # Log and notify
        log_trade_action("OPEN POSITION", symbol, {
            "Type": order_type.upper(),
            "Price": current_price,
            "Amount": amount,
            "Notional": f"${notional:.2f}",
            "Signal Score": f"{signal_score:.1f}",
            "Leverage": f"{LEVERAGE}x",
            "ATR": f"{current_atr:.6f}",
            "Stop Loss": f"{stop_loss_percent:.2f}%",
            "Take Profit": f"{take_profit_percent:.2f}%"
        })
        
        send_telegram(
            f"📈 <b>POSITION OPENED</b>\n\n"
            f"🪙 <b>Coin:</b> {symbol}\n"
            f"📊 <b>Type:</b> {order_type.upper()}\n"
            f"💰 <b>Price:</b> {current_price}\n"
            f"📏 <b>Amount:</b> {amount}\n"
            f"💵 <b>Notional:</b> ${notional:.2f}\n"
            f"📈 <b>Signal Score:</b> {signal_score:.1f}/100\n"
            f"🔥 <b>Leverage:</b> {LEVERAGE}x\n"
            f"📉 <b>ATR:</b> {current_atr:.6f}\n"
            f"🛑 <b>Stop Loss:</b> {stop_loss_percent:.2f}%\n"
            f"🎯 <b>Take Profit:</b> {take_profit_percent:.2f}%"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Order placement error for {symbol}: {e}")
        logger.error(traceback.format_exc())
        return False

def setup_trailing_stop(symbol, position_type, entry_price):
    """Setup trailing stop for position"""
    global trailing_stops
    
    trailing_stops[symbol] = {
        "entry_price": float(entry_price),
        "activation_percent": TRAILING_STOP_ACTIVATION,
        "step_percent": TRAILING_STOP_STEP,      # Her adımda artış miktarı
        "highest_pnl": 0,
        "trailing_distance": TRAILING_STOP_DISTANCE,
        "is_active": False,
        "stop_level": None,
        "last_upgrade_level": 0      # Son stop yükseltme seviyesi
    }
    
    logger.info(f"Trailing stop set for {symbol} ({position_type.upper()}) | Activation: {TRAILING_STOP_ACTIVATION}%")

def update_trailing_stop(symbol, position_type, current_pnl):
    """Update trailing stop level"""
    global trailing_stops
    
    if symbol not in trailing_stops:
        return None
    
    ts = trailing_stops[symbol]
    
    # Check if trailing stop should be activated
    if not ts["is_active"]:
        if current_pnl >= ts["activation_percent"]:
            ts["is_active"] = True
            current_price = exchange.fetch_ticker(symbol)['last']
            
            # İlk etkinleşmede, stop seviyesini giriş seviyesine çek (break-even)
            if position_type.lower() == "long":
                ts["stop_level"] = ts["entry_price"]
            else:  # short
                ts["stop_level"] = ts["entry_price"]
                
            logger.info(f"Trailing stop activated for {symbol} | PnL: {current_pnl:.2f}% | Stop: Break-even")
    
    # Actif olduğunda, her %5 artış için stopu yükselt
    elif ts["is_active"]:
        # Upgrade seviyelerini kontrol et (8, 13, 18, 23, ...)
        current_upgrade_level = int((current_pnl - ts["activation_percent"]) / ts["step_percent"])
        
        if current_upgrade_level > ts["last_upgrade_level"]:
            ts["last_upgrade_level"] = current_upgrade_level
            current_price = exchange.fetch_ticker(symbol)['last']
            
            # Yeni stop seviyesi = giriş fiyatı + (upgrade level * step percent)
            new_stop_percent = current_upgrade_level * ts["step_percent"]
            
            if position_type.lower() == "long":
                # Long pozisyonlarda, giriş fiyatından new_stop_percent kadar yukarı
                price_change = ts["entry_price"] * (new_stop_percent / 100)
                new_stop = ts["entry_price"] + price_change
                ts["stop_level"] = new_stop
                
                logger.info(f"Trailing stop upgraded for {symbol} | New Stop: +{new_stop_percent:.1f}% | PnL: {current_pnl:.2f}%")
            else:  # short
                # Short pozisyonlarda, giriş fiyatından new_stop_percent kadar aşağı
                price_change = ts["entry_price"] * (new_stop_percent / 100)
                new_stop = ts["entry_price"] - price_change
                ts["stop_level"] = new_stop
                
                logger.info(f"Trailing stop upgraded for {symbol} | New Stop: -{new_stop_percent:.1f}% | PnL: {current_pnl:.2f}%")
    
    return ts["stop_level"]

def check_trailing_stop_hit(symbol, position_type):
    """Check if trailing stop is hit"""
    if symbol not in trailing_stops or not trailing_stops[symbol]["is_active"]:
        return False
    
    ts = trailing_stops[symbol]
    current_price = exchange.fetch_ticker(symbol)['last']
    
    if position_type.lower() == "long":
        if current_price <= ts["stop_level"]:
            # Stop seviyesi için ham kâr hesapla
            entry_price = ts["entry_price"]
            stop_pnl = ((ts["stop_level"] - entry_price) / entry_price) * 100
            
            logger.info(f"Trailing stop hit! {symbol} ({position_type.upper()}) | "
                        f"Price: {current_price} | Stop: {ts['stop_level']} | Locked PnL: {stop_pnl:.2f}%")
            return True
    else:  # short
        if current_price >= ts["stop_level"]:
            # Stop seviyesi için ham kâr hesapla
            entry_price = ts["entry_price"]
            stop_pnl = ((entry_price - ts["stop_level"]) / entry_price) * 100
            
            logger.info(f"Trailing stop hit! {symbol} ({position_type.upper()}) | "
                        f"Price: {current_price} | Stop: {ts['stop_level']} | Locked PnL: {stop_pnl:.2f}%")
            return True
    
    return False

def check_daily_pnl_limit():
    """Check if daily balance increase limit is reached"""
    global initial_daily_balance, current_balance
    
    if initial_daily_balance == 0:
        return False
    
    # Bakiye artış yüzdesini hesapla
    balance_increase_percent = ((current_balance - initial_daily_balance) / initial_daily_balance) * 100
    
    if balance_increase_percent >= 10.0:  # %10 veya daha fazla artış
        return True
    return False

def reset_daily_balance():
    """Reset daily balance tracking at midnight"""
    global initial_daily_balance, current_balance, last_reset_date, daily_limit_notified
    
    current_date = datetime.now().date()
    
    # Eğer gün değiştiyse ve henüz sıfırlanmadıysa
    if last_reset_date != current_date:
        # Günlük raporu gönder
        send_daily_balance_report()
        
        # Güncel bakiyeyi yükle ve günlük başlangıç olarak ayarla
        load_balance()
        initial_daily_balance = ACCOUNT_BALANCE
        current_balance = ACCOUNT_BALANCE
        daily_limit_notified = False
        last_reset_date = current_date
        
        logger.info(f"Daily balance tracking reset for new day: {current_date} | Starting balance: ${initial_daily_balance:.2f}")

def send_daily_balance_report():
    """Send daily balance report to Telegram"""
    global initial_daily_balance, current_balance
    
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    if initial_daily_balance > 0:
        balance_change_percent = ((current_balance - initial_daily_balance) / initial_daily_balance) * 100
        balance_change_amount = current_balance - initial_daily_balance
    else:
        balance_change_percent = 0
        balance_change_amount = 0
    
    emoji = "📈" if balance_change_percent > 0 else "📉" if balance_change_percent < 0 else "➖"
    
    send_telegram(
        f"{emoji} <b>GÜNLÜK BAKİYE RAPORU</b>\n\n"
        f"📅 <b>Tarih:</b> {current_date}\n"
        f"💰 <b>Başlangıç:</b> ${initial_daily_balance:.2f}\n"
        f"💰 <b>Güncel:</b> ${current_balance:.2f}\n"
        f"📊 <b>Değişim:</b> {balance_change_percent:+.2f}% (${balance_change_amount:+.2f})\n"
        f"{'🎯 Günlük hedef aşıldı!' if balance_change_percent >= 10.0 else '🔄 Yeni güne devam...'}"
    )

def check_midnight_reset():
    """Check if it's time for midnight reset"""
    current_time = datetime.now()
    
    # Saat 23:59 kontrolü
    if current_time.hour == 23 and current_time.minute == 59:
        reset_daily_balance()
        return True
    return False

def close_position(symbol, position_type):
    """Close an open position"""
    global current_balance, initial_daily_balance
    
    try:
        pos_info = positions.get(symbol)
        if not pos_info:
            logger.warning(f"No position info found for {symbol}")
            return False
            
        amount = pos_info['amount']
        
        # Place closing order - position side parametresini ekleyin
        side = 'SELL' if position_type.lower() == 'long' else 'BUY'
        
        params = {
            'positionSide': 'LONG' if position_type.lower() == 'long' else 'SHORT',
            
        }
        
        order = exchange.create_market_order(
            symbol=symbol,
            side=side,
            amount=amount,
            params=params
        )
        
        # Get current price
        current_price = exchange.fetch_ticker(symbol)['last']
        
        # Calculate final PnL
        entry_price = pos_info['entry_price']
        pnl = check_position_pnl(symbol, position_type, entry_price, current_price, LEVERAGE)
        
        # Güncel bakiyeyi yükle
        load_balance()
        current_balance = ACCOUNT_BALANCE
        
        # Günlük bakiye değişimini hesapla
        if initial_daily_balance > 0:
            daily_balance_change = ((current_balance - initial_daily_balance) / initial_daily_balance) * 100
        else:
            daily_balance_change = 0
        
        # Remove from positions
        del positions[symbol]
        if symbol in trailing_stops:
            del trailing_stops[symbol]
            
        # Add to recently closed
        recently_closed[symbol] = time.time()
        
        # Log and notify
        log_trade_action("CLOSE POSITION", symbol, {
            "Type": position_type.upper(),
            "Entry Price": entry_price,
            "Exit Price": current_price,
            "PnL": f"{pnl:.2f}%",
            "Total Balance": f"${current_balance:.2f}",
            "Daily Change": f"{daily_balance_change:.2f}%",
            "Amount": amount
        })
        
        emoji = "✅" if pnl > 0 else "❌"
        daily_emoji = "🎯" if daily_balance_change >= 10.0 else "📊"
        
        send_telegram(
            f"{emoji} <b>POZİSYON KAPANDI</b>\n\n"
            f"🪙 <b>Coin:</b> {symbol}\n"
            f"📊 <b>Tip:</b> {position_type.upper()}\n"
            f"💰 <b>Giriş:</b> {entry_price}\n"
            f"🎯 <b>Çıkış:</b> {current_price}\n"
            f"{'📈' if pnl > 0 else '📉'} <b>İşlem PnL:</b> {pnl:.2f}%\n"
            f"💵 <b>Toplam Bakiye:</b> ${current_balance:.2f}\n"
            f"{daily_emoji} <b>Günlük Değişim:</b> {daily_balance_change:+.2f}%\n"
            f"{'🚫 Günlük limit aşıldı! Yeni işlem yok.' if daily_balance_change >= 10.0 else ''}"
        )
        
        # Günlük bakiye durumunu logla
        if daily_balance_change >= 10.0:
            logger.info(f"Daily balance limit reached: {daily_balance_change:.2f}% - No more trades today")
        else:
            logger.info(f"Position closed. Balance: ${current_balance:.2f} | Daily change: {daily_balance_change:.2f}%")
        
        return True
        
    except Exception as e:
        logger.error(f"Position closing error for {symbol}: {e}")
        logger.error(traceback.format_exc())
        return False

def check_existing_positions():
    """Check and manage existing positions"""
    for symbol, pos_info in list(positions.items()):
        try:
            position_type = pos_info['type']
            entry_price = pos_info['entry_price']
            current_price = exchange.fetch_ticker(symbol)['last']
            
            # Calculate PnL
            pnl = check_position_pnl(symbol, position_type, entry_price, current_price, LEVERAGE)
            
            stop_loss_percent = pos_info.get('stop_loss_percent', STOP_LOSS_PERCENT)
            take_profit_percent = pos_info.get('take_profit_percent', TAKE_PROFIT_PERCENT)

            # Update trailing stop
            update_trailing_stop(symbol, position_type, pnl)
            
            if check_trailing_stop_hit(symbol, position_type):
                logger.info(f"Closing position due to trailing stop: {symbol}")
                close_position(symbol, position_type)
                continue
                
            # Check dynamic take profit
            if pnl >= take_profit_percent:
                logger.info(f"Dynamic take profit hit: {symbol} ({pnl:.2f}% >= {take_profit_percent:.2f}%)")
                close_position(symbol, position_type)
                continue
                
            # Check dynamic stop loss
            if pnl <= -stop_loss_percent:
                logger.info(f"Dynamic stop loss hit: {symbol} ({pnl:.2f}% <= -{stop_loss_percent:.2f}%)")
                close_position(symbol, position_type)
                continue
                
        except Exception as e:
            logger.error(f"Error checking position for {symbol}: {e}")
            logger.error(traceback.format_exc())

def scan_for_signals(coin_list):
    """Scan all coins for trading signals"""
    global daily_limit_notified, initial_daily_balance, current_balance
    
    # Günlük bakiye limitini kontrol et
    if check_daily_pnl_limit():
        if not daily_limit_notified:
            balance_change = ((current_balance - initial_daily_balance) / initial_daily_balance) * 100
            logger.info(f"Daily balance limit reached ({balance_change:.2f}%). No more trades today.")
            daily_limit_notified = True
        return
    
    for coin in coin_list:
        try:
            # Skip if recently closed or already in position
            if coin in positions or (coin in recently_closed and time.time() - recently_closed[coin] < 300):
                continue
                
            # Get OHLCV data
            df = get_ohlcv_data(coin)
            if df is None or len(df) < 100:
                continue
                
            # Calculate signal score (only logs strong signals)
            score, trend_direction = calculate_total_signal_score(df, coin)
            
            # Place order if signal is strong enough
            if score >= WEAK_SIGNAL_THRESHOLD and trend_direction:
                place_order(coin, trend_direction, score)
                
        except Exception as e:
            logger.error(f"Error scanning {coin}: {e}")
            logger.error(traceback.format_exc())

def main():
    """Main trading loop"""
    global exchange, positions, trailing_stops, recently_closed, ACCOUNT_BALANCE, initial_daily_balance, current_balance, last_reset_date, daily_limit_notified
    
    logger.info("Trading Bot Started")
    
    # Load coin list
    if COIN_LIST_FILE.endswith('.json'):
        coin_list = load_coins_from_json(COIN_LIST_FILE)
    
    if not coin_list:
        logger.error("Failed to load coin list. Exiting...")
        return
    
    logger.info(f"Trading {len(coin_list)} coins with {LEVERAGE}x leverage")
    
    # Initialize exchange
    exchange = initialize_exchange()
    
    # Load balance ve check - sadece bir kez çağır
    if not load_balance():
        logger.error("Failed to load balance. Exiting...")
        return
    
    # Günlük bakiye takibini başlat
    initial_daily_balance = ACCOUNT_BALANCE
    current_balance = ACCOUNT_BALANCE
    last_reset_date = datetime.now().date()
    daily_limit_notified = False
    logger.info(f"Daily balance tracking initialized for {last_reset_date} | Starting balance: ${initial_daily_balance:.2f}")
    
    # Set leverage for all coins
    set_leverage_for_all_coins(coin_list)
    
    # Send start message - ACCOUNT_BALANCE global değişkenini kullan
    send_telegram(
        f"🚀 <b>Trading Bot Started</b>\n\n"
        f"💰 <b>Account Balance:</b> ${ACCOUNT_BALANCE:.2f}\n"
        f"📊 <b>Trading Coins:</b> {len(coin_list)}\n"
        f"🔥 <b>Leverage:</b> {LEVERAGE}x\n"
        f"📈 <b>Günlük Hedef:</b> %10 bakiye artışı"
    )
    
    # Main loop
    while True:
        try:
            # Gece yarısı kontrolü
            reset_daily_balance()
            
            # Check existing positions  
            if positions:
                check_existing_positions()
            
            # Scan for new signals (günlük limit kontrolü içinde)
            scan_for_signals(coin_list)
            
            # Wait for next iteration
            time.sleep(30)
            
        except KeyboardInterrupt:
            logger.warning("Bot stopped by user")
            break
            
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            logger.error(traceback.format_exc())
            time.sleep(30)

if __name__ == "__main__":
    main()