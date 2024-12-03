def bullish(candle):
    return candle['Open'] < candle['Close']

def bearish(candle):
    return candle['Close'] < candle['Open']

def engulfing(df):
    current = df.iloc[len(df)-1]
    past = df.iloc[len(df)-2]
    bullish_id = 0
    bearish_id = 0
    if bullish(current) and bearish(past):
        if current['Open'] < past['Close'] and current['Close'] > past['Open']:
            bullish_id = 1
    if bullish(past) and bearish(current):
        if current['Open'] > past['Close'] and current['Close'] < past['Open']:
            bearish_id = 1
    return bullish_id, bearish_id

def harami(df):
    current = df.iloc[len(df) - 1]
    past = df.iloc[len(df) - 2]
    bullish_id = 0
    bearish_id = 0
    if bullish(current) and bearish(past):
        if past['Close'] < current['Open'] < past['Open']:
            if past['Close'] < current['Close'] < past['Open']:
                bullish_id = 1
    if bullish(past) and bearish(current):
        if past['Open'] < current['Open'] < past['Close']:
            if past['Open'] < current['Close'] < past['Close']:
                bearish_id = 1
    return bullish_id, bearish_id

def hammer_hanging(df):
    current = df.iloc[len(df) - 1]
    past = df.iloc[len(df) - 2]
    past2 = df.iloc[len(df) - 3]
    bullish_id = 0
    bearish_id = 0
    if bearish(past) and bearish(past2):
        if bullish(current):
            if (current['Open'] - current['Low']) > (current['High'] - current['Close']):
                bullish_id = 1
    if bullish(past) and bullish(past2):
        if bearish(current):
            if (current['Close'] - current['Low']) >= 2 * (current['High'] - current['Open']):
                bearish_id = 1
    return bullish_id, bearish_id

def candle_pattern(df):
    bullish_engulf, bearish_engulf = engulfing(df)
    bullish_harami, bearish_harami = harami(df)
    bullish_hamhan, bearish_hamhan = hammer_hanging(df)
    bullish = bullish_harami + bullish_hamhan + bullish_engulf
    bearish = bearish_hamhan + bearish_harami + bearish_engulf
    if bullish != 0 and bearish == 0:
        return "Bullish"
    if bullish == 0 and bearish != 0:
        return "Bearish"
    if bullish != 0 and bearish != 0:
        if bullish > bearish:
            return "Bullish"
        else:
            return "Bearish"
    if bullish == 0 and bearish == 0:
        return "None"

def candlestick_bb(df):
    latest = df.iloc[len(df)-1]
    if latest['Close'] > latest['BBTop']:
        return "Overbought"
    if latest['Close'] < latest['BBBot']:
        return "Oversold"
    return "Normal"

def rsi_pattern(df):
    latest = df.iloc[len(df)-1]
    if latest['RSI'] > 70:
        return str(round(latest['RSI'], 2)) + " - Overbought"
    elif latest['RSI'] < 30:
        return str(round(latest['RSI'], 2)) + " - Oversold"
    else:
        return str(round(latest['RSI'], 2)) + " - Normal"
