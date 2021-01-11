import pandas as pd
from pandas.core.frame import DataFrame
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

stocks = ['27', '200', '880', '2282']
#stocks = ['27']
date_key = 'Time'
price_key = 'Last Trade'
date_format = '%Y/%m/%d %H:%M'
mei_file = 'data/raw/mei.csv'
stock_file = 'data/raw/Equities_%s.csv'
train_file = 'data/train/Equities_%s.csv'
beta_file = 'data/raw/beta.csv'

def beta_diff(stock_price, market_price, window):
    result = pd.Series(np.zeros(len(stock_price)))
    for index, value in stock_price[window - 1:].items():
        start = index - (window - 1)
        end = index + 1
        market_return = market_price[start:end].diff().fillna(0)
        stock_return = stock_price[start:end].diff().fillna(0)
        downside_stock_return = stock_return[market_return < 0]
        upside_stock_return = stock_return[market_return > 0]
        downside_market_return = market_return[market_return < 0]
        upside_market_return = market_return[market_return > 0]
        if downside_stock_return.shape[0] == 0 or upside_stock_return.shape[0] == 0:
            continue
        if downside_market_return.shape[0] == 0 or upside_market_return.shape[0] == 0:
            continue
        downside_market_return_var = np.var(downside_market_return.values)
        updside_market_return_var = np.var(upside_market_return.values)
        if downside_market_return_var == 0 or updside_market_return_var == 0:
            continue
        downside_beta = np.cov(downside_stock_return.values, downside_market_return.values) / downside_market_return_var
        upside_beta = np.cov(upside_stock_return.values, upside_market_return.values) / updside_market_return_var
        result[index] =  (downside_beta - upside_beta)[0][1]
    return result

def rsi(price, window):
    gain = price.diff()
    loss = gain.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    rs = gain.ewm(span=window, min_periods=window).mean() / loss.abs().ewm(span=window, min_periods=window).mean()
    return 100 - 100 / (1 + rs)
  
def gen_train_files():
    mei_data = read_data(mei_file)
    mei_rsi = rsi(price=mei_data['Last Trade'], window=20).fillna(0)
    for stock in stocks:
        data = read_data(stock_file % stock)
        data['EMA1'] = data['Last Trade'].ewm(span=5, min_periods=5).mean().fillna(0)
        data['EMA2'] = data['Last Trade'].ewm(span=8, min_periods=8).mean().fillna(0)
        data['EMA3'] = data['Last Trade'].ewm(span=13, min_periods=13).mean().fillna(0)
        data['MEI RSI'] = mei_rsi.fillna(0) 
        data.to_csv(path_or_buf=train_file % stock, date_format=date_format, index=False)

def gen_beta_files():
    mei_data = read_data(mei_file)
    mei_rsi = rsi(price=mei_data['Last Trade'], window=20).fillna(0)
    beta_data = pd.DataFrame(columns = ['Time'])
    for stock in stocks:
        data = read_data(stock_file % stock)
        beta_data = pd.DataFrame(columns = ['Time'])
        beta_data[stock] =  beta_diff(data['Last Trade'], mei_data['Last Trade'][:len(data)], window=20)
    beta_data.to_csv(path_or_buf=beta_file, date_format=date_format, index=False)

def read_data(file):
    date_parser = lambda x: dt.strptime(x, date_format)
    data = pd.read_csv(file, parse_dates=[date_key], date_parser=date_parser)
    return data

def plot_data(data):
    colors = ["blue","orange","green","red","purple","brown","pink","gray","olive","cyan"]
    time_data = data[date_key]
    fig, axes = plt.subplots(
        nrows=7, ncols=2, figsize=(15, 20), dpi=80, facecolor="w", edgecolor="k"
    )
    column_key = data.columns[1:]
    for i in range(len(column_key)):
        key = column_key[i]
        c = colors[i % (len(colors))]
        t_data = data[key]
        t_data.index = time_data
        t_data.head()
        ax = t_data.plot(
            ax=axes[i // 2, i % 2],
            color=c,
            title=key,
            rot=25,
        )
        ax.legend([column_key[i]])
    plt.tight_layout()
    plt.show()

def main():
    gen_train_files()
    gen_beta_files()

if __name__ == '__main__':
    main()
