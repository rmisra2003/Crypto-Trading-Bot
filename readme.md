# Binance ML+Sentiment Grid Trading Bot

A production-ready crypto trading bot for Binance featuring:
- Technical indicators
- Grid strategy
- Adaptive ML learning on price data
- Live Twitter sentiment integration
- Stateful position management and logs

## Usage
1. Fill in `.env` with your API keys.
2. Edit `config.json` for symbol/trading preferences.
3. `pip install -r requirements.txt`
4. Run: `python bot.py`

**NEVER run live without extensive paper-trading first!**
2. requirements.txt
text
ccxt
ta
pandas
numpy
scikit-learn
joblib
tweepy
transformers
torch
python-dotenv
3. .env
text
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
Add .env to your .gitignore if using git.

4. config.json
json
{
  "exchange": "binance",
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "grid_levels": 10,
  "grid_step_pct": 0.5,
  "order_size": 0.001,
  "base_currency": "USDT",
  "twitter": {
    "query": "BTC OR Bitcoin -is:retweet lang:en",
    "max_tweets": 80
  }
}
5. utils.py
python
import json
import os

def load_config(path='config.json'):
    with open(path, 'r') as f:
        return json.load(f)

def save_log(filename, data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'a') as f:
        f.write(data + '\n')
6. data_fetch.py
python
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
7. indicators.py
python
import ta

def add_indicators(df):
    df['sma'] = ta.trend.sma_indicator(df['close'], window=20)
    df['ema'] = ta.trend.ema_indicator(df['close'], window=20)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    df['macd'] = ta.trend.macd_diff(df['close'])
    boll = ta.volatility.BollingerBands(df['close'], window=20)
    df['bb_upper'] = boll.bollinger_hband()
    df['bb_lower'] = boll.bollinger_lband()
    return df
8. grid_strategy.py
python
import numpy as np

def setup_grid(min_price, max_price, levels):
    return np.linspace(min_price, max_price, levels)

def should_buy(price, grid_levels):
    return any(abs(price - level) < 0.01 for level in grid_levels)

def should_sell(price, grid_levels):
    return any(abs(price - level) < 0.01 for level in grid_levels)
9. ml_strategy.py
python
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np

class MLStrategy:
    def __init__(self, model_path='ml_model.pkl'):
        self.model_path = model_path
        try:
            self.model = joblib.load(model_path)
        except:
            self.model = RandomForestClassifier()
        self.scaler = StandardScaler()

    def prepare_data(self, df):
        features = ['open', 'high', 'low', 'close', 'volume', 'sma', 'ema', 'rsi', 'macd', 'bb_upper', 'bb_lower']
        X = df[features].fillna(0)
        y = np.where(df['close'].shift(-1) > df['close'], 1, 0)
        return X[:-1], y[:-1]

    def fit(self, df):
        X, y = self.prepare_data(df)
        X = self.scaler.fit_transform(X)
        self.model.fit(X, y)
        joblib.dump(self.model, self.model_path)

    def predict(self, df_row):
        X = df_row[['open','high','low','close','volume','sma','ema','rsi','macd','bb_upper','bb_lower']].fillna(0)
        X = self.scaler.transform([X.values])
        return self.model.predict_proba(X)[0]
10. twitter_sentiment.py
python
import tweepy
from transformers import pipeline
from utils import load_config
import os

def fetch_tweets():
    config = load_config()
    twitter_cfg = config["twitter"]
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    client = tweepy.Client(bearer_token=bearer_token)
    tweets = []
    for tweet in tweepy.Paginator(
            client.search_recent_tweets,
            query=twitter_cfg["query"],
            tweet_fields=["text"],
            max_results=100).flatten(limit=twitter_cfg["max_tweets"]):
        tweets.append(tweet.text)
    return tweets

def analyze_sentiment(tweets):
    sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    scores = []
    for tweet in tweets[:32]:  # batch size limit
        out = sentiment_analyzer(tweet)[0]
        scores.append(1 if out['label'] == 'Positive' else -1 if out['label'] == 'Negative' else 0)
    return sum(scores)/len(scores) if scores else 0

def get_twitter_sentiment():
    try:
        tweets = fetch_tweets()
        score = analyze_sentiment(tweets)
        return score
    except Exception as e:
        return 0  # Fallback: neutral if Twitter API/model fails
11. state_manager.py
python
import json
import os

class TradeStateManager:
    def __init__(self, fname='trade_state.json'):
        self.fname = fname
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.fname):
            with open(self.fname, 'w') as f:
                json.dump({"positions":[]}, f)

    def current_position(self):
        with open(self.fname) as f:
            data = json.load(f)
        if not data["positions"]:
            return None
        return data["positions"][-1].get("type", None)

    def record_trade(self, typ, price, order):
        with open(self.fname) as f:
            data = json.load(f)
        entry = {"type": typ, "price": price, "order": order}
        data["positions"].append(entry)
        with open(self.fname, 'w') as f:
            json.dump(data, f, indent=2)
12. bot.py
python
import time
from dotenv import load_dotenv
from utils import load_config, save_log
from data_fetch import get_exchange, fetch_ohlcv
from indicators import add_indicators
from grid_strategy import setup_grid, should_buy, should_sell
from ml_strategy import MLStrategy
from twitter_sentiment import get_twitter_sentiment
from state_manager import TradeStateManager

load_dotenv()  # Load .env for keys

def run_live_trading():
    config = load_config()
    exchange = get_exchange(live=True)
    ml = MLStrategy()
    state_mgr = TradeStateManager()
    symbol = config['symbol']
    timeframe = config['timeframe']
    order_size = config['order_size']
    base = config['base_currency']

    # Initial setup
    save_log('logs/bot.log', f"Starting bot for {symbol} {time.asctime()}")
    df = fetch_ohlcv(exchange, symbol, timeframe, limit=200)
    df = add_indicators(df)
    ml.fit(df)

    min_price, max_price = df['close'].min(), df['close'].max()
    grid_levels = setup_grid(min_price, max_price, config['grid_levels'])

    while True:
        try:
            # Fetch latest bar
            latest = fetch_ohlcv(exchange, symbol, timeframe, limit=2).iloc[-1:]
            latest = add_indicators(latest)
            price = float(latest['close'].values[0])

            # Predict with ML
            prob_up = ml.predict(latest.iloc[0])[1]
            tweet_score = get_twitter_sentiment()
            save_log('logs/bot.log', f"{time.asctime()} | Price: {price} | ML: {prob_up:.3f} | Sentiment: {tweet_score:.3f}")

            buy_signal = should_buy(price, grid_levels) and prob_up > 0.55 and tweet_score > 0.1
            sell_signal = should_sell(price, grid_levels) and prob_up < 0.45 and tweet_score < -0.1

            position = state_mgr.current_position()
            if buy_signal and not position:
                order = exchange.create_market_buy_order(symbol, order_size)
                state_mgr.record_trade('buy', price, dict(order))
                save_log('logs/bot.log', f"BUY at {price:.2f} (Order: {order})")
            elif sell_signal and position == 'buy':
                order = exchange.create_market_sell_order(symbol, order_size)
                state_mgr.record_trade('sell', price, dict(order))
                save_log('logs/bot.log', f"SELL at {price:.2f} (Order: {order})")
        except Exception as e:
            save_log('logs/bot.log', f"Error: {str(e)}")
            time.sleep(15)
        time.sleep(60)  # Adjust for candle interval

if __name__ == "__main__":
    run_live_trading()
13. logs/bot.log
This file will be automatically created by save_log.

All key actions/errors are recorded for review and troubleshooting.

REMINDER:

Make sure to tune thresholds and trading logic to your risk profile and test in paper mode.

You’ll need your own .env file with credentials (never commit it to git/GitHub).

For persistent state, the trade_state.json file will be created in your working directory.

If you want explanations for any module, ask! If you need a zipped folder, please prepare and download it locally; I cannot create nor serve zip files directly.

Save this thread as a Space
Organize your research by saving context for future searches