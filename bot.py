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
