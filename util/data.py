import pandas as pd
from pandas.core.frame import DataFrame
import lstm.config as cfg
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
 
def get_daily_return(file):
    date_key = 'Time'
    price_key = 'Last Trade'
    date_parser = lambda x: dt.strptime(x, cfg.date_format)
    data = pd.read_csv(file, parse_dates=[date_key], date_parser=date_parser)
    starting_price = data.groupby(data[date_key].dt.date).first().drop(columns=[date_key]).reset_index(level=[date_key])
    ending_price = data.groupby(data[date_key].dt.date).last().drop(columns=[date_key]).reset_index(level=[date_key])
    daily_return = pd.DataFrame(columns = ['Time', 'Starting Price', 'Ending Price', 'Return'])
    daily_return['Time'] = starting_price[date_key]
    daily_return['Starting Price'] = starting_price[price_key]
    daily_return['Ending Price'] = ending_price[price_key]
    daily_return['Return'] = (daily_return['Ending Price'] - daily_return['Starting Price']) / daily_return['Starting Price']
    return daily_return

def get_beta_difference():
    market_return = get_daily_return(file='data/mei.csv')
    positive_market_return = market_return[market_return.Return > 0]
    negative_market_return = market_return[market_return.Return < 0]
    equities = ['27', '200', '880', '2282']
    result = pd.DataFrame(columns = ['Stock', 'Beta Difference'])
    for equity in equities:
        stock_return = get_daily_return(file='data/Equities_%s.csv' % equity)      
        downside_stock_return = stock_return[stock_return.Time.isin(negative_market_return.Time)]
        downside_stock_return_values = downside_stock_return['Return'].values
        upside_stock_return = stock_return[stock_return.Time.isin(positive_market_return.Time)]
        upside_stock_return_values = upside_stock_return['Return'].values
        negative_market_return_values = negative_market_return['Return'].values[:len(downside_stock_return)]
        positive_market_return_values = positive_market_return['Return'].values[:len(upside_stock_return)]
        downside_beta = np.cov(downside_stock_return_values, negative_market_return_values) / np.var(negative_market_return_values)
        upside_beta = np.cov(upside_stock_return_values, positive_market_return_values) / np.var(positive_market_return_values)
        beta_difference = (downside_beta - upside_beta)[0][1]
        result = result.append({'Stock': equity, 'Beta Difference': beta_difference}, ignore_index=True)
    return result

def data_preprocessing():
    date_parser = lambda x: dt.strptime(x, cfg.date_format)
    data = pd.read_csv(cfg.data_file, parse_dates=['Time'], date_parser=date_parser)
    data['MA5'] = data['Last Trade'].rolling(window=5).mean().fillna(0)
    data['MA10'] = data['Last Trade'].rolling(window=10).mean().fillna(0)
    data['MA20'] = data['Last Trade'].rolling(window=20).mean().fillna(0)
    data['VOL'] = data['Last Trade'].rolling(window=10).std().fillna(0)
    data['EMA20'] = data['Last Trade'].ewm(span=20, adjust=False).mean().fillna(0)
    data.to_csv(path_or_buf=cfg.data_file, date_format=cfg.date_format, index=False)
    return data

def plot_data(data):
    data = pd.read_csv(cfg.data_file)
    time_data = data[cfg.date_key]
    fig, axes = plt.subplots(
        nrows=7, ncols=2, figsize=(15, 20), dpi=80, facecolor="w", edgecolor="k"
    )
    for i in range(len(cfg.feature_keys)):
        key = cfg.feature_keys[i]
        c = cfg.colors[i % (len(cfg.colors))]
        t_data = data[key]
        t_data.index = time_data
        t_data.head()
        ax = t_data.plot(
            ax=axes[i // 2, i % 2],
            color=c,
            title=key,
            rot=25,
        )
        ax.legend([cfg.feature_keys[i]])
    plt.tight_layout()
    plt.show()

def main():
    print(get_beta_difference())

if __name__ == '__main__':
    main()
