import pandas as pd
from datetime import datetime, time, timedelta, date
import calendar

def closest(df):
    today = pd.to_datetime(date.today())
    if today.weekday() == 5:
        today = today - timedelta(1)
    if today.weekday() == 6:
        today = today - timedelta(2)
    try:
        end_idx = df[df['Date'] == today].index[0]
    except IndexError:
        end_idx = len(df)
        today = df.iloc[len(df)-1]['Date']
    return end_idx, today

def find_idx(df, months):
    default_space = months * 21
    end_idx, today = closest(df)
    prev_month = today.month - months
    prev_year = today.year
    if prev_month <= 0:
        prev_month += 12
        prev_year -= 1
    if today.day <= calendar.monthrange(prev_year, prev_month)[1]:
        prev_today = pd.to_datetime(datetime(prev_year, prev_month, today.day))
    else:
        prev_today = pd.to_datetime(datetime(prev_year, prev_month, calendar.monthrange(prev_year, prev_month)[1]))
    if prev_today.weekday() == 5:
        prev_today = prev_today + timedelta(2)
    if prev_today.weekday() == 6:
        prev_today = prev_today + timedelta(1)
    try:
        start_idx = df[df['Date'] == prev_today].index[0]
    except IndexError:
        start_idx = end_idx - default_space
        if start_idx < 0:
            start_idx = 0
    return start_idx, end_idx, today

def write_label(df):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    labels = []
    indexes = []
    if len(df) > 30:
        if len(df) > 100:
            step = 10
        else:
            step = 6
    else:
        step = 3
    i = 0
    while i < len(df):
        indexes.append(i)
        date1 = df.iloc[i]['Date']
        i += step
        month = months[date1.month - 1]
        if date1.day < 10:
            label = "0" + str(date1.day) + "-" + month
        else:
            label = str(date1.day) + "-" + month
        labels.append(label)
    return indexes, labels

def format_vol(volume):
    if volume < 1000:
        return str(volume)
    elif volume < 1000000:
        vol = volume/1000
        return str(round(vol,3)) + 'K'
    elif volume < 1000000000:
        vol = volume / 1000000
        return str(round(vol,3)) + 'M'
    else:
        vol = volume / 1000000000
        return str(round(vol, 3)) + 'B'