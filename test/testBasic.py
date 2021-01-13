# from backtesting import Backtest, Strateg
import backtrader
from indicators import Indicator
import pandas as pd
import numpy as np
import csv

limit_data = 2000
def removeBreakTimes(path):
    outpath = './temp.csv'
    input = open(path, 'r')
    output = open(outpath, 'w', newline='')
    writer = csv.writer(output)
    for row in csv.reader(input):
        if "12:" not in row[0]:
            writer.writerow(row)
    input.close()
    output.close()
    return outpath

def addTimeHeader(path):
    f = open(path, 'r')
    r = 'Time' + f.read()
    f.close()
    f = open(path, 'w')
    f.write(r)
    f.close()

def loadStockData(path):
    # load the data, generate a DataFrame with the data time for index
    readCSV = pd.read_csv(path)

    maindata = readCSV.to_numpy()[:, 1:].astype(np.float32)
    # Adjust the format to match Backtesting requirements (see pd.Dataframe())
    maindata_adjusted = np.zeros((len(maindata),6))
    for i in range(1,len(maindata)):
        maindata_adjusted[i,3] = maindata[i,0]
        maindata_adjusted[i,0] = maindata[i-1,0]
        maindata_adjusted[i,1] = max(maindata_adjusted[i,0], maindata_adjusted[i,3])
        maindata_adjusted[i,2] = min(maindata_adjusted[i,0], maindata_adjusted[i,3])
        maindata_adjusted[i,4] = maindata_adjusted[i,3]
    maindata_adjusted[:,5] = maindata[:,1]
    # LIMIT ROWS TO limit_data
    maindata_adjusted = maindata_adjusted[-limit_data:]

    dates = readCSV.to_numpy()[:, 0]
    dates_adjusted = dates[-limit_data:]

    stock = pd.DataFrame(maindata_adjusted, index=pd.DatetimeIndex(dates_adjusted),
                         columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
    stock.to_csv('temp.csv')
    addTimeHeader('temp.csv')
    return stock

def LOAD(arr):
    # simple function transfer the buy and sell signal to _indicator array
    arr = pd.Series(arr.tolist())
    return pd.Series(arr)

# strategy for KDJ
class UnifiedStrategy(backtrader.Strategy):
    def init(self):
        x = Indicator('./data/Equities_27.csv',limit_data)
        x.bollinger(2.5)
        #x.mean_reversion(0.09)
        x.macd(False, window=20, trend_ma=100)
        #x.ma()
        x.rsi(14,20)
        x.kdj()
        #x2 = Indikeppar('./data/Equities_27.csv','./data/Equities_200.csv',limit_data)
        #x2.keppar(20, 10)

        # Input: array of the buy&sell signal
        # BOLLINGER
        self.buyS_boll = x.data['Bollinger_Buy'].to_numpy()
        self.sellS_boll = x.data['Bollinger_Sell'].to_numpy()
        self.s_boll = self.I(LOAD, self.sellS_boll, name='sellSIGNAL_BOLL')
        self.b_boll = self.I(LOAD, self.buyS_boll, name='buySIGNAL_BOLL')

        # MACD
        self.buyS_macd = x.data['MACD_Buy'].to_numpy()
        self.sellS_macd = x.data['MACD_Sell'].to_numpy()
        self.s_macd = self.I(LOAD, self.sellS_macd, name='sellSIGNAL_macd')
        self.b_macd = self.I(LOAD, self.buyS_macd, name='buySIGNAL_macd')

        # RSI
        self.buyS_rsi = x.data['RSI_Buy'].to_numpy()
        self.sellS_rsi = x.data['RSI_Sell'].to_numpy()
        self.s_rsi = self.I(LOAD, self.sellS_rsi, name='sellSIGNAL_rsi')
        self.b_rsi = self.I(LOAD, self.buyS_rsi, name='buySIGNAL_rsi')

        # KDJ
        self.buyS_kdj = x.data['KDJ_Buy'].to_numpy()
        self.sellS_kdj = x.data['KDJ_Sell'].to_numpy()
        self.s_kdj = self.I(LOAD, self.sellS_kdj, name='sellSIGNAL_kdj')
        self.b_kdj = self.I(LOAD, self.buyS_kdj, name='buySIGNAL_kdj')

        # keppar
        #self.buyS_keppar = x2.data['keppar_Buy'].to_numpy()
        #self.sellS_keppar = x2.data['keppar_Sell'].to_numpy()
        #self.s_keppar = self.I(LOAD, self.sellS_keppar, name='sellSIGNAL_keppar')
        #self.b_keppar = self.I(LOAD, self.buyS_keppar, name='buySIGNAL_keppar')

        # signal weighting
        self.s = 0
        self.b = 0
        self.s += 0 * self.s_boll + 0 * self.s_macd + 0 * self.s_rsi + 0 * self.s_kdj# + 1 * self.s_keppar
        self.b += 0 * self.b_boll + 0 * self.b_macd + 0 * self.b_rsi + 0 * self.b_kdj# + 1 * self.b_keppar

    def next(self):
        if self.s >= 1:
            self.sell()
        elif self.b >= 1:
            self.buy()

if __name__ == '__main__':
    path = './data/Equities_27.csv'
    path = removeBreakTimes(path)
    # Load your stock data through this function
    # The data must contain value of 'Open','High','Low','Close', although you may not use it for strategy
    stockData = loadStockData(path)

    # Use the backtest function to get the represent your buy&sell process
    # You can change your strategy for the backtesting
    bt = Backtest(stockData, UnifiedStrategy, cash=10000, commission=.002, exclusive_orders=True)
    stats = bt.run()
    bt.plot()
    print(stats)
