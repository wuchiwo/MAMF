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
mei_file = '../data/raw/mei.csv'
stock_file = '../data/raw/Equities_%s.csv'
train_file = '../data/train/Equities_%s.csv'

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
  
def data_preprocessing(rawdata: DataFrame) -> DataFrame:
    # mei_data = read_data(mei_file)
    mei_data = rawdata
    mei_rsi = rsi(price=mei_data['Last Trade'], window=20).fillna(0)
    # for stock in stocks:
    # data = read_data(stock_file % stock)
    data = pd.DataFrame(rawdata)
    data['MA1'] = data['Last Trade'].rolling(window=5).mean().fillna(0)
    data['MA2'] = data['Last Trade'].rolling(window=8).mean().fillna(0)
    data['MA3'] = data['Last Trade'].rolling(window=13).mean().fillna(0)
    data['EMA1'] = data['Last Trade'].ewm(span=5, min_periods=5).mean().fillna(0)
    data['EMA2'] = data['Last Trade'].ewm(span=8, min_periods=8).mean().fillna(0)
    data['EMA3'] = data['Last Trade'].ewm(span=13, min_periods=13).mean().fillna(0)
    data['MEI RSI'] = mei_rsi.fillna(0) 
    data['Beta Diff'] = beta_diff(data['Last Trade'], mei_data['Last Trade'][:len(data)], window=20)
    # data.to_csv(path_or_buf=train_file % stock, date_format=date_format, index=False)
    return data

def read_data(file):
    date_parser = lambda x: dt.strptime(x, date_format)
    data = pd.read_csv(file, parse_dates=[date_key], date_parser=date_parser)
    return data

# def format_data(data):

#     def loadStockData(path):
#     # load the data, generate a DataFrame with the data time for index
#     readCSV = pd.read_csv(path)

#     maindata = readCSV.to_numpy()[:, 1:].astype(np.float32)
#     # Adjust the format to match Backtesting requirements (see pd.Dataframe())
#     maindata_adjusted = np.zeros((len(maindata),6))
#     for i in range(1,len(maindata)):
#         maindata_adjusted[i,3] = maindata[i,0]
#         maindata_adjusted[i,0] = maindata[i-1,0]
#         maindata_adjusted[i,1] = max(maindata_adjusted[i,0], maindata_adjusted[i,3])
#         maindata_adjusted[i,2] = min(maindata_adjusted[i,0], maindata_adjusted[i,3])
#         maindata_adjusted[i,4] = maindata_adjusted[i,3]
#     maindata_adjusted[:,5] = maindata[:,1]
#     # LIMIT ROWS TO limit_data
#     maindata_adjusted = maindata_adjusted[-limit_data:]

#     dates = readCSV.to_numpy()[:, 0]
#     dates_adjusted = dates[-limit_data:]

#     stock = pd.DataFrame(maindata_adjusted, index=pd.DatetimeIndex(dates_adjusted),
#                          columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
#     stock.to_csv('temp.csv')
#     addTimeHeader('temp.csv')
#     return stock

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
    np.seterr('raise')
    mei_data = read_data(mei_file)
    data_preprocessing(mei_data)

if __name__ == '__main__':
    stocks = ['27', '200', '880', '2282']
    for stock in stocks:
        df = pd.read_csv('../data/train/Equities_%s.csv' % stock)
        df = data_preprocessing(df)
        df.to_csv('../data/Beta/Equities_%s.csv' % stock)
