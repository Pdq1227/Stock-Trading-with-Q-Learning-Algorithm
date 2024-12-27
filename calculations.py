import numpy as np


def sma(df, num):
    mov_avg = []
    for i in range(len(df)):
        if i < num-1:
            mov_avg.append(np.nan)
        else:
            mov_avg.append(df.iloc[i - (num-1):i + 1]['close'].mean())
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


def rsi(df, periods):
    close_delta = df['close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    rsi_dx = ma_up / ma_down
    rsi_dx = 100 - (100 / (1 + rsi_dx))
    return rsi_dx


def preprocess_draw(df):
    df['Date'] = df['time']
    df['Volume'] = df['volume']
    df['SMA50'] = sma(df, 50)
    df['SMA100'] = sma(df, 100)
    df['RSI'] = rsi(df, 14)
    df['BBBot_Close'], df['BBMid_Close'], df['BBTop_Close'] = bollinger_bands(df, 'close', 20, 2)
    df.dropna(inplace=True)
    df.drop(columns=['time', 'volume'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def preprocess_model(df):
    df['Date'] = df['time']
    df['Open'] = round(df['open'] * 1000)
    df['High'] = round(df['high'] * 1000)
    df['Low'] = round(df['low'] * 1000)
    df['Close'] = round(df['close'] * 1000)
    df['Volume'] = df['volume']

    # data['Change'] = (data['Close'] - data['Close'].shift(1)) / data['Close'].shift(1) * 100
    # data['State'] = np.where(data['Change'] < -3.0, 0, np.where(data['Change'] < -1.5, 1, np.where(data['Change'] < 0, 2, np.where(data['Change'] < 1.5, 3, np.where(data['Change'] < 3.0, 4, 5)))))

    df['O'] = (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1) * 100
    df['H'] = (df['High'] - df['Open']) / df['Open'] * 100
    df['L'] = (df['Low'] - df['Open']) / df['Open'] * 100
    df['C'] = (df['Close'] - df['Open']) / df['Open'] * 100
    # data['V'] = (data['Volume'] - data['Volume'].shift(1)) / data['Volume'].shift(1) * 100


    df['RSI'] = rsi(df, 14)
    # data['BBBot_Close'], data['BBMid_Close'], data['BBTop_Close'] = bollinger_bands(data, 'Close', 20, 1)
    # data['BBBot_RSI'], data['BBMid_RSI'], data['BBTop_RSI'] = bollinger_bands(data, 'RSI', 20, 1)

    df.dropna(inplace=True)
    df.drop(columns=['time', 'volume'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # states = classify(data)
    # data['State'] = states

    df['Action'] = ''
    df['Action1'] = -1
    df['ActiveAction'] = ''
    df['Cash'] = 0
    df['Reward'] = 0
    return df