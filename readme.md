


# 🚀 Crypto Trading Bot

A Python-based crypto trading bot that combines **technical analysis, machine learning, grid trading, and sentiment analysis** to make automated trading decisions.

---

## 📌 Overview

This bot monitors a configured trading pair, evaluates market conditions using multiple signals, and executes trades when all conditions align.

It integrates:

* 📊 Technical Indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
* 🤖 Machine Learning (RandomForestClassifier)
* 📉 Grid Trading Strategy
* 🐦 Twitter/X Sentiment Analysis

---

## ✨ Features

* Fetches OHLCV market data using `ccxt`
* Computes key technical indicators using `ta`
* Trains a machine learning model on recent market data
* Implements a grid-based trading strategy
* Uses Twitter sentiment as an additional signal filter
* Logs all activity for monitoring and debugging
* Stores trade state locally

---

## 🧠 How It Works

1. Loads API credentials from `.env`
2. Loads trading configuration from `config.json`
3. Connects to the exchange
4. Fetches market data and computes indicators
5. Trains ML model on historical data
6. Generates grid levels
7. Runs continuous loop:

   * Fetch latest data
   * Recalculate indicators
   * Predict market movement
   * Analyze sentiment
   * Execute buy/sell orders if conditions match

---

## 🏗️ Project Structure

```
bot.py                 # Main trading loop
data_fetch.py          # Exchange connection & data retrieval
indicators.py          # Technical indicators
grid_strategy.py       # Grid trading logic
ml_strategy.py         # ML model training & prediction
twitter_sentiment.py   # Sentiment analysis
state_manager.py       # Trade state handling
utils.py               # Helper functions
config.json            # Bot configuration
requirements.txt       # Dependencies
```

---

## ⚙️ Requirements

* Python 3.10+
* Exchange API credentials (e.g., Binance)
* Twitter/X Bearer Token

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔐 Configuration

### 1. Environment Variables

Create a `.env` file:

```env
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

⚠️ **Important:**

* Never commit real credentials
* Use minimal permissions
* Prefer testnet/paper trading first

---

### 2. Bot Settings (`config.json`)

```json
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
```

---

## ▶️ Running the Bot

```bash
python bot.py
```

---

## 📊 Strategy Logic

The bot uses **three filters together**:

### 1. Grid Condition

Trades only when price is near predefined grid levels.

### 2. ML Condition

* Buy → High probability of upward movement
* Sell → Low probability

### 3. Sentiment Condition

* Buy → Positive sentiment
* Sell → Negative sentiment

**Default thresholds:**

```text
Buy  → prob_up > 0.55 AND sentiment > 0.1
Sell → prob_up < 0.45 AND sentiment < -0.1
```

---

## 📁 Outputs

* `logs/bot.log` → Logs, signals, and errors
* `trade_state.json` → Trade history/state
* `ml_model.pkl` → Saved ML model

---

## ⚠️ Limitations

* Executes **real market orders**
* No backtesting pipeline yet
* ML model is basic (no validation)
* Limited error handling (fees, slippage, API failures)
* Sentiment model may be slow on first run

---

## 🔮 Future Improvements

* Add backtesting module
* Support testnet/paper trading
* Improve risk management
* Save scaler/model pipeline
* Add alerts & monitoring
* Write unit tests

---

## 📌 Disclaimer

> This project is for **educational purposes only**.
> Cryptocurrency trading is highly risky.
> Use at your own risk.

---

## 💡 Tech Stack

* Python
* ccxt
* ta (Technical Analysis)
* scikit-learn
* Transformers (for sentiment analysis)

---



---

