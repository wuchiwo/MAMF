import pandas as pd
import lstm.config as cfg
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def read_data():
    date_parser = lambda x: datetime.strptime(x, cfg.date_format)
    data = pd.read_csv(cfg.data_file, parse_dates=['Time'], date_parser=date_parser)
    #print(data.groupby(pd.Grouper(key='Time',freq='M')).sum())
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
    data = read_data()
    plot_data(data)

if __name__ == '__main__':
    main()
