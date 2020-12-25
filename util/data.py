import pandas as pd
from pandas.core.frame import DataFrame
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
 
stocks = ['27', '200', '880', '2282']
date_key = 'Time'
price_key = 'Last Trade'
date_format = '%Y/%m/%d %H:%M'
mei_file = 'data/raw/mei.csv'
stock_file = 'data/raw/Equities_%s.csv'
train_file = 'data/train/Equities_%s.csv'

def get_daily_return(file):
    data = read_data(file)
    starting_price = data.groupby(data[date_key].dt.date).first().drop(columns=[date_key]).reset_index(level=[date_key])
    ending_price = data.groupby(data[date_key].dt.date).last().drop(columns=[date_key]).reset_index(level=[date_key])
    daily_return = pd.DataFrame(columns = ['Time', 'Starting Price', 'Ending Price', 'Return'])
    daily_return['Time'] = starting_price[date_key]
    daily_return['Starting Price'] = starting_price[price_key]
    daily_return['Ending Price'] = ending_price[price_key]
    daily_return['Return'] = (daily_return['Ending Price'] - daily_return['Starting Price']) / daily_return['Starting Price']
    return daily_return

def get_beta_difference():
    market_return = get_daily_return(file=mei_file)
    positive_market_return = market_return[market_return.Return > 0]
    negative_market_return = market_return[market_return.Return < 0]
    result = pd.DataFrame(columns = ['Stock', 'Beta Difference'])
    for stock in stocks:
        stock_return = get_daily_return(file=stock_file % stock)      
        downside_stock_return = stock_return[stock_return.Time.isin(negative_market_return.Time)]
        downside_stock_return_values = downside_stock_return['Return'].values
        upside_stock_return = stock_return[stock_return.Time.isin(positive_market_return.Time)]
        upside_stock_return_values = upside_stock_return['Return'].values
        negative_market_return_values = negative_market_return['Return'].values[:len(downside_stock_return)]
        positive_market_return_values = positive_market_return['Return'].values[:len(upside_stock_return)]
        downside_beta = np.cov(downside_stock_return_values, negative_market_return_values) / np.var(negative_market_return_values)
        upside_beta = np.cov(upside_stock_return_values, positive_market_return_values) / np.var(positive_market_return_values)
        beta_difference = (downside_beta - upside_beta)[0][1]
        result = result.append({'Stock': stock, 'Beta Difference': beta_difference}, ignore_index=True)
    return result

def data_preprocessing():
    for stock in stocks:
        data = read_data(stock_file % stock)
        data['MA60'] = data['Last Trade'].rolling(window=60).mean().fillna(0)
        data['MA120'] = data['Last Trade'].rolling(window=120).mean().fillna(0)
        data['MA180'] = data['Last Trade'].rolling(window=180).mean().fillna(0)
        data['VOL60'] = data['Last Trade'].rolling(window=60).std().fillna(0)
        data['EMA20'] = data['Last Trade'].ewm(span=20, adjust=False).mean().fillna(0)
        data['RSI2'] = data['Last Trade'].ewm(span=20, adjust=False).mean().fillna(0)
        data.to_csv(path_or_buf=train_file % stock, date_format=date_format, index=False)

def read_data(file):
    date_parser = lambda x: dt.strptime(x, date_format)
    data = pd.read_csv(file, parse_dates=[date_key], date_parser=date_parser)
    return data

def plot_data(data, feature_keys):
    colors = ["blue","orange","green","red","purple","brown","pink","gray","olive","cyan"]
    time_data = data[date_key]
    fig, axes = plt.subplots(
        nrows=7, ncols=2, figsize=(15, 20), dpi=80, facecolor="w", edgecolor="k"
    )
    for i in range(len(feature_keys)):
        key = feature_keys[i]
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
        ax.legend([feature_keys[i]])
    plt.tight_layout()
    plt.show()

def main():
    data_preprocessing()
    print(get_beta_difference())

if __name__ == '__main__':
    main()
