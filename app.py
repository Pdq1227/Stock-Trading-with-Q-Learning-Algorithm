import math
import tkinter as tk
import tkinter.font as tfont
import warnings
from tkinter import *
from tkinter.ttk import Combobox
import numpy as np
import os
from datetime import datetime


import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from vnstock3 import Vnstock

import calculations
import formatting
import model

curr_path = os.path.dirname(__file__)
try:
    os.makedirs('outputs')
except FileExistsError:
    pass
except PermissionError:
    pass
except Exception as e:
    pass
output_path = curr_path + '//outputs//'

warnings.filterwarnings("ignore")
pd.options.mode.chained_assignment = None

stock_market = Vnstock().stock(source='VCI')
data_draw = None
canvas = None
today = datetime.today().strftime('%Y-%m-%d')

# Settings for chart
plt.rcdefaults()
plt.rcParams.update({'axes.facecolor': 'black'})


# All function for GUI
def on_move_model(event):
    if event.inaxes:
        try:
            xdata = math.ceil(event.xdata)
            ydata = data_draw.iloc[xdata]
            date_txt = str(ydata['Date'].day) + "-" + str(ydata['Date'].month) + "-" + str(ydata['Date'].year)
            ohlc_txt = '%AC: ' + str(round(ydata['Capital_Change'],2)) + ' Buy-and-Hold: ' + str(round(ydata['Price_Change'],2))
            date_lb.config(text=date_txt)
            ohlc_lb.config(text=ohlc_txt)
        except Exception as e:
            pass


def on_move_chart(event):
    if event.inaxes:
        try:
            xdata = math.ceil(event.xdata)
            ydata = data_draw.iloc[xdata]
            date_txt = str(ydata['Date'].day) + "-" + str(ydata['Date'].month) + "-" + str(ydata['Date'].year)
            ohlc_txt = 'O ' + str(ydata['open']) + ' H ' + str(ydata['high']) + ' L ' + str(ydata['low']) + ' C ' + str(ydata['close']) + ' (' + str(round((ydata['close']-data_draw.iloc[xdata-1]['close'])/data_draw.iloc[xdata-1]['close']*100,2)) + '%)'
            bb20_txt = 'BB20 ' + str(round(ydata['BBBot_Close'],2)) + ' ' + str(round(ydata['BBMid_Close'],2)) + ' ' + str(round(ydata['BBTop_Close'],2))
            sma50_txt = 'SMA50 ' + str(round(ydata['SMA50'],2))
            sma100_txt = 'SMA100 ' + str(round(ydata['SMA100'],2))
            rsi_txt = 'RSI ' + str(round(ydata['RSI'],2))
            volume_txt = 'Volume ' + formatting.format_vol(ydata['Volume'])
            date_lb.config(text=date_txt)
            ohlc_lb.config(text=ohlc_txt)
            bb20_lb.config(text=bb20_txt)
            sma50_lb.config(text=sma50_txt)
            sma100_lb.config(text=sma100_txt)
            rsi_lb.config(text=rsi_txt)
            vol_lb.config(text=volume_txt)
        except Exception as e:
            pass


def add_stock():
    if ticker_in.get() is not None:
        ticker = ticker_in.get()
    else:
        print('Nothing was inputted')
        return
    stock_id = Vnstock().stock(symbol=ticker, source='VCI')
    df = stock_id.quote.history(start='2019-01-01', end='2024-12-26')
    pass


def load_model():
    # Initialize
    global data_draw, canvas

    if stock_in.get() != "":
        ticker = stock_in.get().split()[0].upper()
    else:
        print('No stock was inputted')
        return
    dir_path = output_path + ticker
    if os.path.exists(dir_path):
        print('Stock ' + ticker + ' found')
    else:
        print('Stock ' + ticker + ' not trained')
        return
    csv_path = dir_path + '//csv//Test'
    test_rois_trained = np.load(dir_path+'//test_rois.npy').tolist()
    max_test_roi_id = test_rois_trained.index(max(test_rois_trained))
    data_draw = pd.read_csv(csv_path + '//Test'+str(max_test_roi_id+1)+'.csv', parse_dates=[5]).reset_index()

    # Hidden irrelevant data
    if canvas is not None:
        canvas.get_tk_widget().pack_forget()
    date_lb.config(text='')
    ohlc_lb.config(text='')
    bb20_lb.config(text='')
    sma50_lb.config(text='')
    sma100_lb.config(text='')
    rsi_lb.config(text='')
    vol_lb.config(text='')

    # Draw chart
    xticks, labels = formatting.write_label(data_draw)
    matplotlib.rc('axes', edgecolor='white')
    colors = ['#39FF14' if (data_draw.iloc[i]['Close'] >= data_draw.iloc[i]['Open']) else '#FD1C03' for i in
              range(len(data_draw))]
    fig = Figure(figsize=(17.2, 9.25), facecolor='black')
    spec = gridspec.GridSpec(ncols=1, nrows=1, left=0.03, right=0.997, bottom=0.03, top=0.995, hspace=0)
    ax1 = fig.add_subplot(spec[0])
    ax1.tick_params(axis='x', colors='white')
    ax1.tick_params(axis='y', colors='white')
    ax1.plot(data_draw['index'], data_draw['Price_Change'], c='white', linewidth=1)
    ax1.plot(data_draw['index'], data_draw['Capital_Change'], c='yellow', linewidth=1)
    ax1.set_xlim(-1, len(data_draw))
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(labels)
    ax1.xaxis.grid(color='white', linewidth=0.3, linestyle='-')

    # Connect chart
    canvas = FigureCanvasTkAgg(fig, master=chart_canvas)
    canvas.draw()
    canvas.get_tk_widget().pack()
    canvas.mpl_connect('motion_notify_event', on_move_model)


def training():
    #Initialize
    global data_draw, canvas

    # Getting data
    if stock_in.get() != "":
        ticker = stock_in.get().split()[0].upper()
    else:
        ticker = 'VNINDEX'
    result_path = output_path + ticker

    # All exceptions: Trained stock, Index (HSX and HNX) and No stock found
    if os.path.exists(result_path):
        print('Stock ' + ticker + ' already trained')
        print('Redirecting to load trained model for this stock')
        load_model()
        return
    if ticker == 'VNINDEX' or ticker == 'HNXINDEX':
        print('Cannot perform learning on index')
        return
    try:
        stock_id = Vnstock().stock(symbol=ticker, source='VCI')
    except TypeError:
        print('Stock' + ticker + ' not found')
        return

    df_train = stock_id.quote.history(start='2019-01-01', end='2023-12-31')
    df_test = stock_id.quote.history(start='2024-01-01', end=today)
    data_train = calculations.preprocess_model(df_train)
    data_test = calculations.preprocess_model(df_test)
    cfg = model.Config(ticker)

    # Train and test on model
    q_model = model.Model(cfg)
    q_model.train(data_train)
    q_model.test(data_test)
    load_model()


def chart():
    #Initialize
    global data_draw, canvas

    # Getting data
    if stock_in.get() != "":
        ticker = stock_in.get().split()[0].upper()
    else:
        ticker = 'VNINDEX'
    try:
        stock_id = Vnstock().stock(symbol=ticker, source='VCI')
    except TypeError:
        print('Stock not found')
        return
    df = stock_id.quote.history(start='2019-01-01', end=today)
    data = calculations.preprocess_draw(df)
    chart_width, line_width = 0.3, 0.7
    start_idx, end_idx, latest = formatting.find_idx(data, 9)
    data_draw = data.iloc[start_idx:end_idx + 1].reset_index().drop(columns='index', axis=1).reset_index()

    # Hidden irrelevant data
    if canvas is not None:
        canvas.get_tk_widget().pack_forget()
    date_lb.config(text='')
    ohlc_lb.config(text='')
    bb20_lb.config(text='')
    sma50_lb.config(text='')
    sma100_lb.config(text='')
    rsi_lb.config(text='')
    vol_lb.config(text='')

    # Draw charts
    xticks, labels = formatting.write_label(data_draw)
    matplotlib.rc('axes', edgecolor='white')
    colors = ['#39FF14' if (data_draw.iloc[i]['close'] >= data_draw.iloc[i]['open']) else '#FD1C03' for i in
              range(len(data_draw))]
    fig = Figure(figsize=(17.2, 9.25), facecolor='black')
    spec = gridspec.GridSpec(ncols=1, nrows=3, left=0.03, right=0.997,
                             bottom=0.03, top=0.995, hspace=0, height_ratios=[4, 1.5, 1])
    ax1 = fig.add_subplot(spec[0])
    ax1.tick_params(axis='x', colors='white')
    ax1.tick_params(axis='y', colors='white')
    ax1.bar(x=data_draw['index'], height=data_draw['close'] - data_draw['open'], bottom=data_draw['open'], linewidth=2,
            width=chart_width, edgecolor=colors, color=colors)
    ax1.bar(x=data_draw['index'], height=data_draw['high'] - data_draw['low'], bottom=data_draw['low'],
            linewidth=line_width, width=0, edgecolor=colors, color=colors)
    # ax1.plot(data_draw['index'], data_draw['SMA5'], c='gray', linewidth=1, label="SMA5")
    ax1.plot(data_draw['index'], data_draw['SMA50'], c='white', linewidth=1, label="SMA50")
    ax1.plot(data_draw['index'], data_draw['SMA100'], c='yellow', linewidth=1, label="SMA200")
    ax1.plot(data_draw['index'], data_draw['BBTop_Close'], c='cyan', linewidth=1)
    ax1.plot(data_draw['index'], data_draw['BBMid_Close'], c='darkorange', linewidth=1, label="SMA20")
    ax1.plot(data_draw['index'], data_draw['BBBot_Close'], c='cyan', linewidth=1)
    ax1.fill_between(data_draw['index'], data_draw['BBBot_Close'], data_draw['BBTop_Close'],where=data_draw['BBTop_Close'] >= data_draw['BBBot_Close'], facecolor='cyan', alpha=0.12)
    ax1.set_xlim(-1, len(data_draw))
    ax1.set_xticks(xticks)
    ax1.set_xticklabels([])
    ax1.xaxis.grid(color='white', linewidth=0.3, linestyle='-')
    ax2 = fig.add_subplot(spec[1])
    ax2.tick_params(axis='x', colors='white')
    ax2.tick_params(axis='y', colors='white')
    ax2.plot(data_draw['index'], data_draw['RSI'], c='cyan', linewidth=1, label='RSI')
    ax2.set_xticks(xticks)
    ax2.set_xticklabels([])
    ax2.set_xlim(-1, len(data_draw))
    ax2.xaxis.grid(color='white', linewidth=0.3, linestyle='-')
    ax3 = fig.add_subplot(spec[2])
    ax3.tick_params(axis='x', colors='white', labelsize=8)
    ax3.tick_params(axis='y', colors='white')
    ax3.bar(x=data_draw['index'], height=data_draw['Volume'], linewidth=1,
            width=chart_width * 2, edgecolor=colors, color=colors)
    ax3.set_xticks(xticks)
    ax3.set_xticklabels(labels)
    ax3.set_xlim(-1, len(data_draw))
    ax3.xaxis.grid(color='white', linewidth=0.3, linestyle='-')

    # Connect chart
    canvas = FigureCanvasTkAgg(fig, master=chart_canvas)
    canvas.draw()
    canvas.get_tk_widget().pack()
    canvas.mpl_connect('motion_notify_event', on_move_chart)

    # Update stock name
    stock_name.config(text=ticker)

# App skeleton
root = tk.Tk()
root.title('Stock')
root.configure(width=1920, height=1030)
root.state('zoomed')
search_canvas = tk.Canvas(root, height=40, width=1920, bg="light grey")
search_canvas.grid(row=0, column=0, columnspan=2)
value_canvas = tk.Canvas(root, height=40, width=1720, bg="#f0f0f0")
value_canvas.grid(row=1, column=0)
chart_canvas = tk.Canvas(root, height=925, width=1720, bg="#f0f0f0")
chart_canvas.grid(row=2, column=0)
bookmark_canvas = tk.Canvas(root, height=969, width=190, bg="light grey")
bookmark_canvas.grid(row=1, column=1, rowspan=2)


# Fonts
light_font = tfont.Font(family="Body", size=15, weight="bold")
light2_font = tfont.Font(family="Body", size=11, weight="bold")
but_font = tfont.Font(family="Body", size=12)

# Searchbar
stock_lb = tk.Label(root, text="Stock", width=10, bg="light grey")
stock_lb.config(font=light_font)
idx_in = StringVar(root)
stock_in = StringVar(root)
options = ['VNINDEX','HNXINDEX']
tickers = stock_market.listing.all_symbols()['ticker'].tolist()
organ_names = stock_market.listing.all_symbols()['organ_name'].tolist()
for i in range(len(stock_market.listing.all_symbols())):
    option = tickers[i] + ' - ' + organ_names[i]
    options.append(option)
drop_stock = Combobox(root, textvariable=stock_in, values=options)
drop_stock.config(width=100)
search_canvas.create_window(340, 22, window=stock_lb)
search_canvas.create_window(690, 22, window=drop_stock)
chart_button = tk.Button(root, text="Chart", command=lambda: chart(), bg="light grey")
chart_button.config(font=but_font)
search_canvas.create_window(1040, 22, window=chart_button)
model_button = tk.Button(root, text="Train", command=lambda: training(), bg="light grey")
model_button.config(font=but_font)
search_canvas.create_window(1105, 22, window=model_button)
load_button = tk.Button(root, text="Load", command=lambda: load_model(), bg="light grey")
load_button.config(font=but_font)
search_canvas.create_window(1170, 22, window=load_button)

# Information Pane
stock_name = tk.Label(root, text="",width=10, bg="#f0f0f0", anchor="center")
stock_name.config(font=light_font)
date_lb = tk.Label(root, text="", width=10, bg="#f0f0f0", anchor="center")
date_lb.config(font=light_font)
ohlc_lb = tk.Label(root, text="", width=40, bg="#f0f0f0", anchor="center")
ohlc_lb.config(font=light_font)
bb20_lb = tk.Label(root, text="", width=25, bg="#f0f0f0", anchor="center")
bb20_lb.config(font=light_font)
sma50_lb = tk.Label(root, text="", width=13, bg="#f0f0f0", anchor="center")
sma50_lb.config(font=light_font)
sma100_lb = tk.Label(root, text="", width=13, bg="#f0f0f0", anchor="center")
sma100_lb.config(font=light_font)
rsi_lb = tk.Label(root, text="", width = 9, bg="#f0f0f0", anchor="center")
rsi_lb.config(font=light_font)
vol_lb = tk.Label(root, text="", width=15, bg="#f0f0f0", anchor="center")
vol_lb.config(font=light_font)

value_canvas.create_window(70, 22, window=stock_name)
value_canvas.create_window(200, 22, window=date_lb)
value_canvas.create_window(510, 22, window=ohlc_lb)
value_canvas.create_window(910, 22, window=bb20_lb)
value_canvas.create_window(1150, 22, window=sma50_lb)
value_canvas.create_window(1318, 22, window=sma100_lb)
value_canvas.create_window(1470, 22, window=rsi_lb)
value_canvas.create_window(1625, 22, window=vol_lb)

# Bookmark Pane
ticker_in = StringVar(root)
bookmark_lb = tk.Label(root, text="Bookmark",width=15, bg="light grey", anchor="center")
bookmark_lb.config(font=light_font)
bookmark_canvas.create_window(95, 22, window=bookmark_lb)
add_options = ['VNINDEX','HNXINDEX'] + tickers
add_in = Combobox(root, textvariable=ticker_in, values=add_options)
add_in.config(width=10)
add_button = tk.Button(root, text="Add ticker", command=lambda: add_stock, bg="light grey")
add_button.config(font=but_font)
bookmark_canvas.create_window(50, 955, window=add_in)
bookmark_canvas.create_window(140, 955, window=add_button)
root.mainloop()
