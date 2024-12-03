from tkinter.ttk import Combobox
import patterns
import calculations
import formatting
import math
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from tkinter import *
import tkinter as tk
import tkinter.font as tfont
from matplotlib import gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import warnings

warnings.filterwarnings("ignore")
pd.options.mode.chained_assignment = None

# App skeleton
root = tk.Tk()
root.title('Technical Analysis for Stock')
root.configure(width=1920, height=1030)
root.state('zoomed')
canvas0 = tk.Canvas(root, height=50, width=1920, bg="light grey")
canvas0.grid(row=0, column=0, columnspan=2)
canvas1 = tk.Canvas(root, height=980, width=1690, bg="light grey")
canvas1.grid(row=1, column=0)
canvas2 = tk.Canvas(root, height=980, width=220, bg="light grey")
canvas2.grid(row=1, column=1)

# Fonts
light_font = tfont.Font(family="Body", size=15, weight="bold")
light2_font = tfont.Font(family="Body", size=11, weight="bold")
but_font = tfont.Font(family="Body", size=12)


def change_menu(event):
    global idx, options
    if idx_in.get() != idx:
        idx = idx_in.get().upper()
        options = []
    all_stock_path = "https://raw.githubusercontent.com/Pdq1227/Data/main/Stock_Market/" + idx + "/" + idx + ".csv"
    data = pd.read_csv(all_stock_path)
    for i in range(len(data)):
        options.append(data.iloc[i]['Stock'])
    drop_stock.config(values=options)

# Searchbar
idx_name = tk.Label(root, text="Index", width=10, bg="light grey")
idx_name.config(font=light_font)
stock_name = tk.Label(root, text="Stock", width=10, bg="light grey")
stock_name.config(font=light_font)
path1 = "https://raw.githubusercontent.com/Pdq1227/Data/main/Stock_Market/HOSE/HOSE.csv"
stock = pd.read_csv(path1)
idx_in = StringVar(root)
stock_in = StringVar(root)
options = []
drop_idx = Combobox(root, textvariable=idx_in, values=["HOSE", "HNX"])
drop_stock = Combobox(root, textvariable=stock_in, values=options)
drop_idx.bind("<<ComboboxSelected>>", change_menu)
drop_stock.config(width=9)
drop_idx.config(width=9)
canvas0.create_window(400, 25, window=idx_name)
canvas0.create_window(600, 25, window=stock_name)
canvas0.create_window(480, 25, window=drop_idx)
canvas0.create_window(680, 25, window=drop_stock)

# Information Pane
label = tk.Label(root, width=10, bg="light grey")
label.config(font=light_font)
date_lb = tk.Label(root, text="Date", width=10, bg="light grey", anchor="e")
date_lb.config(font=light2_font)
date_in = tk.Entry(root, width=11)
open_lb = tk.Label(root, text="Open", width=10, bg="light grey", anchor="e")
open_lb.config(font=light2_font)
open_in = tk.Entry(root, width=11)
close_lb = tk.Label(root, text="Close", width=10, bg="light grey", anchor="e")
close_lb.config(font=light2_font)
close_in = tk.Entry(root, width=11)
high_lb = tk.Label(root, text="High", width=10, bg="light grey", anchor="e")
high_lb.config(font=light2_font)
high_in = tk.Entry(root, width=11)
low_lb = tk.Label(root, text="Low", width=10, bg="light grey", anchor="e")
low_lb.config(font=light2_font)
low_in = tk.Entry(root, width=11)
rsi_lb = tk.Label(root, text="RSI", width=10, bg="light grey", anchor="e")
rsi_lb.config(font=light2_font)
rsi_in = tk.Entry(root, width=11)
sma5 = tk.Label(root, text="MA5", width=10, bg="light grey", anchor="e")
sma5.config(font=light2_font)
sma5_in = tk.Entry(root, width=11)
sma20 = tk.Label(root, text="MA20", width=10, bg="light grey", anchor="e")
sma20.config(font=light2_font)
sma20_in = tk.Entry(root, width=11)
sma50 = tk.Label(root, text="MA50", width=10, bg="light grey", anchor="e")
sma50.config(font=light2_font)
sma50_in = tk.Entry(root, width=11)
sma200 = tk.Label(root, text="MA200", width=10, bg="light grey", anchor="e")
sma200.config(font=light2_font)
sma200_in = tk.Entry(root, width=11)

canvas2.create_window(110, 150, window=label)
canvas2.create_window(50, 200, window=date_lb)
canvas2.create_window(145, 200, window=date_in)
canvas2.create_window(50, 230, window=open_lb)
canvas2.create_window(145, 230, window=open_in)
canvas2.create_window(50, 260, window=close_lb)
canvas2.create_window(145, 260, window=close_in)
canvas2.create_window(50, 290, window=high_lb)
canvas2.create_window(145, 290, window=high_in)
canvas2.create_window(50, 320, window=low_lb)
canvas2.create_window(145, 320, window=low_in)
canvas2.create_window(50, 350, window=sma5)
canvas2.create_window(145, 350, window=sma5_in)
canvas2.create_window(50, 380, window=sma20)
canvas2.create_window(145, 380, window=sma20_in)
canvas2.create_window(50, 410, window=sma50)
canvas2.create_window(145, 410, window=sma50_in)
canvas2.create_window(50, 440, window=sma200)
canvas2.create_window(145, 440, window=sma200_in)
canvas2.create_window(50, 470, window=rsi_lb)
canvas2.create_window(145, 470, window=rsi_in)

# Global attributes
data_draw = None
stock = None
idx = "HOSE"
last_months = None
canvas = None

# Settings for chart
plt.rcdefaults()
plt.rcParams.update({'axes.facecolor': 'black'})

def on_move(event):
    if event.inaxes:
        try:
            xdata = math.ceil(event.xdata)
            ydata = data_draw.iloc[xdata]
            latest_d = ydata['Date'].day
            latest_m = ydata['Date'].month
            latest_y = ydata['Date'].year
            date_on = str(latest_d) + "-" + str(latest_m) + "-" + str(latest_y)
            date_in.delete(0, END)
            date_in.insert(0, date_on)
            open_in.delete(0, END)
            open_in.insert(0, str(ydata['Open']))
            close_in.delete(0, END)
            close_in.insert(0, str(ydata['Close']))
            high_in.delete(0, END)
            high_in.insert(0, str(ydata['High']))
            low_in.delete(0, END)
            low_in.insert(0, str(ydata['Low']))
            rsi_in.delete(0, END)
            rsi_in.insert(0, str(round(ydata['RSI'], 2)))
            sma5_in.delete(0, END)
            sma5_in.insert(0, str(round(ydata['SMA5'], 2)))
            sma20_in.delete(0, END)
            sma20_in.insert(0, str(round(ydata['BBMid_Close'], 2)))
            sma50_in.delete(0, END)
            sma50_in.insert(0, str(round(ydata['SMA50'], 2)))
            sma200_in.delete(0, END)
            sma200_in.insert(0, str(round(ydata['SMA200'], 2)))
        except IndexError:
            print("Out of bound")
        except TypeError:
            print("Out of bound")

def format_df(df):
    df['SMA5'] = calculations.sma(df, 5)
    df['SMA50'] = calculations.sma(df, 50)
    df['SMA200'] = calculations.sma(df, 200)
    df['BBBot_Close'], df['BBMid_Close'], df['BBTop_Close'] = calculations.bollinger_bands(df, 'Close',20, 2)
    df['RSI'] = calculations.rsi(df)
    df['BBBot_RSI'], df['BBMid_RSI'], df['BBTop_RSI'] = calculations.bollinger_bands(df, 'RSI', 20, 1)
    df['BBBot2_RSI'], df['BBMid_RSI'], df['BBTop2_RSI'] = calculations.bollinger_bands(df, 'RSI', 20, 2)
    df['RSIBot'] = 30
    df['RSITop'] = 70
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    return df


def candlestick(months):
    global stock, idx, data_draw, last_months, canvas
    if stock_in.get() != "" and idx_in.get() != "":
        if stock != stock_in.get():
            stock = stock_in.get()
            idx = idx_in.get()
            if canvas is not None:
                canvas.get_tk_widget().pack_forget()
        elif months != last_months:
            last_months = months
            if canvas is not None:
                canvas.get_tk_widget().pack_forget()
        else:
            return
    try:
        path = "https://raw.githubusercontent.com/Pdq1227/Data/main/Stock_Market/" \
               + idx.upper() + "/" + stock.upper() + ".csv"
        df = pd.read_csv(path)
    except AttributeError:
        print("Input missing")
    except:
        print(path)
        print("Error: File not found")
        return
    data = format_df(df)
    chart_width, line_width = formatting.width_format(months)
    start_idx, end_idx, latest = formatting.find_idx(data, months)
    data_draw = data.iloc[start_idx:end_idx + 1].reset_index().drop(columns='index', axis=1).reset_index()

    # Improve
    xticks, labels = formatting.write_label(data_draw)
    matplotlib.rc('axes', edgecolor='white')
    colors = ['#39FF14' if (data_draw.iloc[i]['Close'] >= data_draw.iloc[i]['Open']) else '#FD1C03' for i in
              range(len(data_draw))]
    fig = Figure(figsize=(16.9, 9.8), facecolor='black')
    spec = gridspec.GridSpec(ncols=1, nrows=3, left=0.026, right=0.997,
                             bottom=0.05, top=0.97, hspace=0, height_ratios=[4, 1.5, 1])
    ax1 = fig.add_subplot(spec[0])
    ax1.tick_params(axis='x', colors='white')
    ax1.tick_params(axis='y', colors='white')
    ax1.bar(x=data_draw['index'], height=data_draw['Close'] - data_draw['Open'], bottom=data_draw['Open'], linewidth=2,
            width=chart_width, edgecolor=colors, color=colors)
    ax1.bar(x=data_draw['index'], height=data_draw['High'] - data_draw['Low'], bottom=data_draw['Low'],
            linewidth=line_width, width=0, edgecolor=colors, color=colors)
    ax1.plot(data_draw['index'], data_draw['SMA5'], c='gray', linewidth=1, label="SMA5")
    ax1.plot(data_draw['index'], data_draw['SMA50'], c='white', linewidth=1, label="SMA50")
    ax1.plot(data_draw['index'], data_draw['SMA200'], c='yellow', linewidth=1, label="SMA200")
    ax1.plot(data_draw['index'], data_draw['BBTop_Close'], c='cyan', linewidth=1)
    ax1.plot(data_draw['index'], data_draw['BBMid_Close'], c='darkorange', linewidth=1, label="SMA20")
    ax1.plot(data_draw['index'], data_draw['BBBot_Close'], c='cyan', linewidth=1)
    ax1.fill_between(data_draw['index'], data_draw['BBBot_Close'], data_draw['BBTop_Close'], where = data_draw['BBTop_Close'] >= data_draw['BBBot_Close'], facecolor='cyan', alpha=0.12)
    ax1.set_xlim(-1, len(data_draw))
    ax1.set_xticks(xticks)
    ax1.set_xticklabels([])
    ax1.xaxis.grid(color='white', linewidth=0.3, linestyle='-')
    if months < 12:
        title = stock.upper() + ' - ' + str(months) + 'M'
    else:
        title = stock.upper() + ' - ' + str(months//12) + 'Y'
    ax1.set_title(title, color='white', size=12)
    ax1.legend(labelcolor="white")
    ax2 = fig.add_subplot(spec[1])
    ax2.tick_params(axis='x', colors='white')
    ax2.tick_params(axis='y', colors='white')
    ax2.plot(data_draw['index'], data_draw['RSI'], c='cyan', linewidth=1, label='RSI')
    ax2.plot(data_draw['index'], data_draw['BBBot2_RSI'], c='yellow', linewidth=1)
    ax2.plot(data_draw['index'], data_draw['BBBot_RSI'], c='white', linewidth=1)
    ax2.plot(data_draw['index'], data_draw['BBMid_RSI'], c='orange', linewidth=1, label = 'RSI-MA20')
    ax2.plot(data_draw['index'], data_draw['BBTop_RSI'], c='white', linewidth=1)
    ax2.plot(data_draw['index'], data_draw['BBTop2_RSI'], c='yellow', linewidth=1)

    # ax2.plot(data_draw['index'], data_draw['RSITop'], c='darkorange', linewidth=0.7, linestyle='-.')
    # ax2.plot(data_draw['index'], data_draw['RSIBot'], c='darkorange', linewidth=0.7, linestyle='-.')
    ax2.set_xticks(xticks)
    ax2.set_xticklabels([])
    ax2.set_xlim(-1, len(data_draw))
    ax2.xaxis.grid(color='white', linewidth=0.3, linestyle='-')
    ax1.legend(labelcolor="white")
    ax3 = fig.add_subplot(spec[2])
    ax3.tick_params(axis='x', colors='white', labelsize=8)
    ax3.tick_params(axis='y', colors='white')
    ax3.bar(x=data_draw['index'], height=data_draw['Volume'], linewidth=1,
            width=chart_width, edgecolor=colors, color=colors)
    ax3.set_xticks(xticks)
    ax3.set_xticklabels(labels)
    ax3.set_xlim(-1, len(data_draw))
    ax3.xaxis.grid(color='white', linewidth=0.3, linestyle='-')
    # Update canvas
    canvas = FigureCanvasTkAgg(fig, master=canvas1)
    canvas.draw()
    canvas.get_tk_widget().pack()
    canvas.mpl_connect('motion_notify_event', on_move)

    # Update and move to global
    idx_mkt = stock.upper() + " - " + idx.upper()
    latest_d = data_draw.iloc[len(data_draw) - 1]['Date'].day
    latest_m = data_draw.iloc[len(data_draw) - 1]['Date'].month
    latest_y = data_draw.iloc[len(data_draw) - 1]['Date'].year
    latest_day = str(latest_d) + "-" + str(latest_m) + "-" + str(latest_y)
    label.config(text=idx_mkt)

    date_in.delete(0, END)
    date_in.insert(0, latest_day)
    open_in.delete(0, END)
    open_in.insert(0, str(data_draw.iloc[len(data_draw) - 1]['Open']))
    close_in.delete(0, END)
    close_in.insert(0, str(data_draw.iloc[len(data_draw) - 1]['Close']))
    high_in.delete(0, END)
    high_in.insert(0, str(data_draw.iloc[len(data_draw) - 1]['High']))
    low_in.delete(0, END)
    low_in.insert(0, str(data_draw.iloc[len(data_draw) - 1]['Low']))
    rsi_in.delete(0, END)
    rsi_in.insert(0, str(round(data_draw.iloc[len(data_draw) - 1]['RSI'], 2)))
    sma5_in.delete(0, END)
    sma5_in.insert(0, str(round(data_draw.iloc[len(data_draw) - 1]['SMA5'], 2)))
    sma20_in.delete(0, END)
    sma20_in.insert(0, str(round(data_draw.iloc[len(data_draw) - 1]['BBMid_Close'], 2)))
    sma50_in.delete(0, END)
    sma50_in.insert(0, str(round(data_draw.iloc[len(data_draw) - 1]['SMA50'], 2)))
    sma200_in.delete(0, END)
    sma200_in.insert(0, str(round(data_draw.iloc[len(data_draw) - 1]['SMA200'], 2)))


# Draw button
but1m = tk.Button(root, text="1M", command=lambda: candlestick(1), bg="light grey")
but1m.config(font=but_font)
canvas0.create_window(850, 27, window=but1m)
but3m = tk.Button(root, text="3M", command=lambda: candlestick(3), bg="light grey")
but3m.config(font=but_font)
canvas0.create_window(900, 27, window=but3m)
but6m = tk.Button(root, text="6M", command=lambda: candlestick(6), bg="light grey")
but6m.config(font=but_font)
canvas0.create_window(950, 27, window=but6m)
but1y = tk.Button(root, text="1Y", command=lambda: candlestick(12), bg="light grey")
but1y.config(font=but_font)
canvas0.create_window(998, 27, window=but1y)

root.mainloop()
