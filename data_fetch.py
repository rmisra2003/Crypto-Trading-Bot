import ccxt
import pandas as pd
import os

def get_exchange(live=True):
    from dotenv import load_dotenv
    load_dotenv()
    import os
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    config = load_config()
    exchange = getattr(ccxt, config['exchange'])({
        'apiKey': api_key,
        'secret': api_secret
    })
    exchange.load_markets()
    return exchange

def fetch_ohlcv(exchange, symbol, timeframe, limit=1000):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

from utils import load_config
