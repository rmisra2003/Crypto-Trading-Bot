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
