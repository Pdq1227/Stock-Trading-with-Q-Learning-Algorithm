import numpy as np

def sma(df, num):
    mov_avg = []
    for i in range(len(df)):
        if i < num-1:
            mov_avg.append(np.nan)
        else:
            mov_avg.append(df.iloc[i - (num-1):i + 1]['Close'].mean())
    return mov_avg

def bollinger_bands(df, column, num, stds):
    bb_top = []
    bb_mid = []
    bb_bot = []
    for i in range(len(df)):
        if i < num-1:
            bb_top.append(np.nan)
            bb_mid.append(np.nan)
            bb_bot.append(np.nan)
        else:
            mid = df.iloc[i - 19:i + 1][column].mean()
            std = df.iloc[i - 19:i + 1][column].std()
            top = mid + stds * std
            bot = mid - stds * std
            bb_top.append(top)
            bb_mid.append(mid)
            bb_bot.append(bot)
    return bb_bot, bb_mid, bb_top

def rsi(df, periods=20):
    close_delta = df['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    rsi_dx = ma_up / ma_down
    rsi_dx = 100 - (100 / (1 + rsi_dx))
    return rsi_dx

