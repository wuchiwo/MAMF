import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as web
import math

pd.set_option('display.min_rows', 255)

class Indicator:
    def __init__(self, filename, limit=0):
        self.data = pd.read_csv(filename)
        if limit != 0:
            self.data = self.data[-limit:]
        self.add_indicators(ma=[2, 5, 20, 50, 100])

    def add_indicators(self, ma=[20, 50, 100]):
        for idx, item in self.data.iterrows():
            for m in ma:
                self.data[str(m) + 'MA'] = self.data['Last Trade'].rolling(window=m).mean()
            self.data['20STD'] = self.data['Last Trade'].rolling(window=20).std()
            self.data['MR_Deviation'] = (- self.data['Last Trade'] + self.data['20MA']) / self.data['20MA']
            # self.data['9EMA'] = self.data['Last Trade'].ewm(span=9, adjust=False).mean()
            self.data['26EMA'] = self.data['Last Trade'].ewm(span=26, adjust=False).mean()
            self.data['12EMA'] = self.data['Last Trade'].ewm(span=12, adjust=False).mean()
            self.data['MACD'] = self.data['12EMA'] - self.data['26EMA']  # - self.data['9EMA']
            self.data['L_n'] = self.data['Last Trade'].rolling(window=9).min()
            self.data['H_n'] = self.data['Last Trade'].rolling(window=9).max()
            self.data['C_n'] = self.data['Last Trade'].rolling(window=1).min()
            self.data['RSV_n'] = (self.data['C_n'] - self.data['L_n']) / (self.data['H_n'] - self.data['L_n']) * 100

    def bollinger(self, sigma=2, show=False):
        self.trend(ma=50)
        for idx, item in self.data.iterrows():
            last_trade = self.data.loc[idx, 'Last Trade']
            self.data['Upper Band'] = self.data['20MA'] + (self.data['20STD'] * sigma)
            self.data['Lower Band'] = self.data['20MA'] - (self.data['20STD'] * sigma)
            self.data.loc[idx, 'Bollinger_Buy'] = (last_trade <= self.data.loc[idx, 'Lower Band']) * \
                                                  self.data.loc[idx, 'Trend_bull']
            self.data.loc[idx, 'Bollinger_Sell'] = (last_trade >= self.data.loc[idx, 'Upper Band']) * \
                                                   self.data.loc[idx, 'Trend_bear']
        if show == True:
            self.data[['Last Trade', '20MA', 'Upper Band', 'Lower Band']].plot(figsize=(12, 6))
            plt2 = plt.twinx()
            plt2.plot(self.data['Bollinger_Buy'], 'bo', markersize=1)
            plt2.plot(self.data['Bollinger_Sell'], 'ro', markersize=1)
            plt.title('Bollinger Band')
            plt.ylabel('Left - Value; Right - Buy = blue, Sell = red')
            plt.show()

    def mean_reversion(self, threshold=0.1, show=False):
        for idx, item in self.data.iterrows():
            self.data.loc[idx, 'MR_Signal'] = True if (self.data.loc[idx, 'MR_Deviation'] > threshold or self.data.loc[
                idx, 'MR_Deviation'] < -threshold) else False
        if show == True:
            self.data[['Last Trade', 'MR_Deviation']].plot(figsize=(12, 6))
            plt2 = plt.twinx()
            plt2.plot(self.data['MR_Signal'], 'go', markersize=1)
            plt.title('Mean Reversion')
            plt.ylabel('Left - Value; Right - mean reversion')
            plt.show()

    def macd(self, show=False, window=7, trend_ma=20):
        self.trend(trend_ma)
        self.data['MACD'] = self.data['MACD'].rolling(window).mean()
        for idx, item in self.data.iterrows():
            try:
                if self.data.loc[idx - 1, 'MACD'] < 0 and self.data.loc[idx, 'MACD'] > 0 \
                        or self.data.loc[idx - 1, 'MACD'] - self.data.loc[idx - 2, 'MACD'] < 0 and self.data.loc[
                    idx, 'MACD'] - self.data.loc[idx - 1, 'MACD'] > 0:
                    self.data.loc[idx, 'MACD_Buy'] = True
                else:
                    self.data.loc[idx, 'MACD_Buy'] = False
            except:
                self.data.loc[idx, 'MACD_Buy'] = None
            try:
                if self.data.loc[idx - 1, 'MACD'] > 0 and self.data.loc[idx, 'MACD'] < 0 \
                        or self.data.loc[idx - 1, 'MACD'] - self.data.loc[idx - 2, 'MACD'] > 0 and self.data.loc[
                    idx, 'MACD'] - self.data.loc[idx - 1, 'MACD'] < 0:
                    self.data.loc[idx, 'MACD_Sell'] = True
                else:
                    self.data.loc[idx, 'MACD_Sell'] = False
            except:
                self.data.loc[idx, 'MACD_Sell'] = None
            self.data.loc[idx, 'MACD_Buy'] *= self.data.loc[idx, 'Trend_bear']
            self.data.loc[idx, 'MACD_Sell'] *= self.data.loc[idx, 'Trend_bull']
        for idx, item in self.data.iterrows():
            if self.data.loc[idx, 'MACD_Buy'] == None:
                self.data.loc[idx, 'MACD_Buy'] = False
            if self.data.loc[idx, 'MACD_Sell'] == None:
                self.data.loc[idx, 'MACD_Sell'] = False
        if show == True:
            self.data[['Last Trade']].plot(figsize=(12, 6))
            plt2 = plt.twinx()
            plt2.plot(self.data['MACD'], 'g--')
            plt2.plot(self.data['MACD_Buy'], 'bo', markersize=1)
            plt2.plot(self.data['MACD_Sell'], 'ro', markersize=1)
            plt.title('MACD')
            plt.ylabel('Left - Value; Right - red=sell, blue=buy, green=macd')
            plt.show()

    def kdj(self, show=False):
        for idx, item in self.data.iterrows():
            try:
                self.data.loc[idx, 'K_n'] = 2 / 3 * self.data.loc[idx - 1, 'K_n'] + 1 / 3 * self.data.loc[idx, 'RSV_n']
                self.data.loc[idx, 'D_n'] = 2 / 3 * self.data.loc[idx - 1, 'D_n'] + 1 / 3 * self.data.loc[idx, 'K_n']
                self.data.loc[idx, 'J_n'] = 3 * self.data.loc[idx, 'K_n'] - 2 * self.data.loc[idx, 'D_n']
                if pd.isnull(self.data.loc[idx, 'K_n']) or pd.isnull(self.data.loc[idx, 'D_n']) or pd.isnull(
                        self.data.loc[idx, 'J_n']):
                    raise Exception
                self.data.loc[idx, 'KDJ_Sell'] = self.data.loc[idx - 1, 'K_n'] < self.data.loc[idx - 1, 'D_n'] and \
                                                 self.data.loc[idx, 'K_n'] > self.data.loc[idx, 'D_n']
                self.data.loc[idx, 'KDJ_Buy'] = self.data.loc[idx - 1, 'K_n'] > self.data.loc[idx - 1, 'D_n'] and \
                                                self.data.loc[idx, 'K_n'] < self.data.loc[idx, 'D_n']
            except:
                self.data.loc[idx, 'K_n'] = 50
                self.data.loc[idx, 'D_n'] = 50
                self.data.loc[idx, 'J_n'] = 50
                self.data.loc[idx, 'KDJ_Buy'] = None
                self.data.loc[idx, 'KDJ_Sell'] = None
        for idx, item in self.data.iterrows():
            if self.data.loc[idx, 'KDJ_Buy'] == None:
                self.data.loc[idx, 'KDJ_Buy'] = False
            if self.data.loc[idx, 'KDJ_Sell'] == None:
                self.data.loc[idx, 'KDJ_Sell'] = False
        if show == True:
            self.data[['Last Trade', 'K_n', 'D_n', 'J_n']].plot(figsize=(12, 6))
            plt2 = plt.twinx()
            plt2.plot(self.data['KDJ_Buy'], 'bo', markersize=1)
            plt2.plot(self.data['KDJ_Sell'], 'ro', markersize=1)
            plt.title('MA')
            plt.ylabel('Left - Value; Right - red=sell, blue=buy')
            plt.show()

    def ma(self, show=False):
        for idx, item in self.data.iterrows():
            try:
                self.data.loc[idx, 'MA_Sell'] = (
                            self.data.loc[idx, '100MA'] - self.data.loc[idx, '20MA'] > 0 and self.data.loc[
                        idx - 1, '100MA'] - self.data.loc[idx - 1, '20MA'] < 0)
                self.data.loc[idx, 'MA_Buy'] = (
                            self.data.loc[idx, '100MA'] - self.data.loc[idx, '20MA'] < 0 and self.data.loc[
                        idx - 1, '100MA'] - self.data.loc[idx - 1, '20MA'] > 0)
            except:
                self.data.loc[idx, 'MA_Buy'] = None
                self.data.loc[idx, 'MA_Sell'] = None
        for idx, item in self.data.iterrows():
            if self.data.loc[idx, 'MA_Buy'] == None:
                self.data.loc[idx, 'MA_Buy'] = False
            if self.data.loc[idx, 'MA_Sell'] == None:
                self.data.loc[idx, 'MA_Sell'] = False
        if show == True:
            self.data[['Last Trade', '20MA', '100MA']].plot(figsize=(12, 6))
            plt2 = plt.twinx()
            plt2.plot(self.data['MA_Buy'], 'bo', markersize=1)
            plt2.plot(self.data['MA_Sell'], 'ro', markersize=1)
            plt.title('MA')
            plt.ylabel('Left - Value; Right - red=sell, blue=buy')
            plt.show()

    def trend(self, ma=50):
        for idx, item in self.data.iterrows():
            try:
                self.data.loc[idx, 'Trend_bull'] = self.data.loc[idx, str(ma) + 'MA'] > self.data.loc[
                    idx - 1, str(ma) + 'MA']
                self.data.loc[idx, 'Trend_bear'] = self.data.loc[idx, str(ma) + 'MA'] < self.data.loc[
                    idx - 1, str(ma) + 'MA']
            except:
                self.data.loc[idx, 'Trend_bull'] = False
                self.data.loc[idx, 'Trend_bear'] = False

    def rsi(self, window=14, trend_ma=5, show=False):
        lower = 0.35
        upper = 0.65
        self.trend(trend_ma)
        for idx, item in self.data.iterrows():
            try:
                self.data.loc[idx, 'Gain'] = self.data.loc[idx, 'Last Trade'] - self.data.loc[idx - 1, 'Last Trade'] if \
                self.data.loc[idx, 'Last Trade'] - self.data.loc[idx - 1, 'Last Trade'] > 0 else 0
                self.data.loc[idx, 'Loss'] = self.data.loc[idx, 'Last Trade'] - self.data.loc[idx - 1, 'Last Trade'] if \
                self.data.loc[idx, 'Last Trade'] - self.data.loc[idx - 1, 'Last Trade'] < 0 else 0
            except:
                self.data.loc[idx, 'Gain'] = 0
                self.data.loc[idx, 'Loss'] = 0
            self.data['GainEMA'] = self.data['Gain'].ewm(span=window).mean()
            self.data['LossEMA'] = self.data['Loss'].abs().ewm(span=window).mean()
            self.data.loc[idx, 'RSI'] = 1 - (
                        1 / (1.0 + (self.data.loc[idx, 'GainEMA'] / self.data.loc[idx, 'LossEMA'])))
            self.data.loc[idx, 'RSI_Buy'] = self.data.loc[idx, 'RSI'] < lower and self.data.loc[idx - 1, 'RSI'] > lower
            self.data.loc[idx, 'RSI_Sell'] = self.data.loc[idx, 'RSI'] > upper and self.data.loc[idx - 1, 'RSI'] < upper
            self.data.loc[idx, 'RSI_Buy'] *= self.data.loc[idx, 'Trend_bear']
            # self.data.loc[idx, 'RSI_Sell'] *= self.data.loc[idx, 'Trend_bull']
        if show == True:
            self.data[['Last Trade']].plot(figsize=(12, 6))
            plt2 = plt.twinx()
            plt2.plot(self.data['RSI'], 'g-', markersize=1)
            plt2.plot(self.data['RSI_Buy'], 'bo', markersize=1)
            plt2.plot(self.data['RSI_Sell'], 'ro', markersize=1)
            plt.title('RSI/100')
            plt.ylabel('Left - Value; Right - red=sell, blue=buy')
            plt.show()


def main():
    filename = "./data/Equities_200.csv"
    x = Indicator(filename,limit=2000)
    x.bollinger(1.5, True)
    #x.mean_reversion(0.09, True)
    #x.macd(True,14,100)
    #x.ma(True)
    #x.rsi(14, 20, show=True)
    #x.kdj(True)



if __name__ == '__main__':
    main()