import ccxt; exchange = ccxt.binance(); ticker = exchange.fetch_ticker("BTC/USDT"); print("BTC:", ticker["last"])
