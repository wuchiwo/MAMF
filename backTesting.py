from backtesting import Backtest, Strategy
from indicators import Indicator
import pandas as pd
import numpy as np


def loadStockData(path):
    # load the data, generate a DataFrame with the data time for index
    readCSV = pd.read_csv(path)
    maindata = readCSV.to_numpy()[:, 1:].astype(np.float32)
    dates = readCSV.to_numpy()[:, 0]

    stock = pd.DataFrame(maindata, index=pd.DatetimeIndex(dates),
                         columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
    return stock


def LOAD(arr):
    # simple function transfer the buy and sell signal to _indicator array
    arr = pd.Series(arr.tolist())
    return pd.Series(arr)


# strategy for KDJ
class KDJstrategy(Strategy):
    def init(self):
        x = Indicator('data/predict-0027.HK.csv')
        x.kdj()

        #
        # Input: array of the buy&sell signal
        #

        self.buyS = x.data['KDJ_Buy'].to_numpy()
        self.sellS = x.data['KDJ_Sell'].to_numpy()
        self.s = self.I(LOAD, self.sellS, name='sellSIGNAL')
        self.b = self.I(LOAD, self.buyS, name='buySIGNAL')

    def next(self):
        if self.s == 1:
            self.sell()
        elif self.b == 1:
            self.buy()


if __name__ == '__main__':
    # Load your stock data through this function
    # The data must contain value of 'Open','High','Low','Close', although you may not use it for strategy
    stockData = loadStockData('data/0027.HK.csv')

    # Use the backtest function to get the represent your buy&sell process
    # You can change your strategy for the backtesting
    bt = Backtest(stockData, KDJstrategy, cash=10000, commission=.002, exclusive_orders=True)
    stats = bt.run()
    bt.plot()
    print(stats)


