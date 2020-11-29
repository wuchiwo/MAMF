# Bollinger Band
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as web
pd.set_option('display.min_rows', 255)

class Indicator:
    def __init__(self, filename):
        self.data = pd.read_csv(filename)
        self.add_indicators()
    
    def add_indicators(self):
        for idx, item in self.data.iterrows():
            self.data['20MA'] = self.data['value'].rolling(window=20).mean()
            self.data['20STD'] = self.data['value'].rolling(window=20).std()
            self.data['100MA'] = self.data['value'].rolling(window=100).mean()
            self.data['MR_Deviation'] = (- self.data['value'] + self.data['20MA']) / self.data['20MA'] 
            #self.data['9EMA'] = self.data['value'].ewm(span=9, adjust=False).mean()
            self.data['26EMA'] = self.data['value'].ewm(span=26, adjust=False).mean()
            self.data['12EMA'] = self.data['value'].ewm(span=12, adjust=False).mean()
            self.data['MACD'] = self.data['12EMA'] - self.data['26EMA']# - self.data['9EMA']

    def bollinger(self, show=False):
        for idx, item in self.data.iterrows():
            self.data['Upper Band'] = self.data['20MA'] + (self.data['20STD'] * 2)
            self.data['Lower Band'] = self.data['20MA'] - (self.data['20STD'] * 2)
            self.data.loc[idx, 'Bollinger_Buy'] = (self.data.loc[idx, 'value'] <= self.data.loc[idx, 'Lower Band'])
            self.data.loc[idx, 'Bollinger_Sell'] = (self.data.loc[idx, 'value'] >= self.data.loc[idx, 'Upper Band'])
        if show == True:
            self.data[['value', '20MA', 'Upper Band', 'Lower Band']].plot(figsize=(12,6))
            plt2 = plt.twinx()
            plt2.plot(self.data['Bollinger_Buy'], 'bo', markersize=1)
            plt2.plot(self.data['Bollinger_Sell'], 'ro', markersize=1)
            plt.title('Bollinger Band')
            plt.ylabel('Left - Value; Right - Buy = blue, Sell = red')
            plt.show()
    
    def mean_reversion(self, threshold=0.1, show=False):
        for idx, item in self.data.iterrows():
            self.data.loc[idx, 'MR_Signal'] = True if (self.data.loc[idx, 'MR_Deviation'] > threshold or self.data.loc[idx, 'MR_Deviation'] < -threshold) else False
        if show == True:
            self.data[['value', 'MR_Deviation']].plot(figsize=(12,6))
            plt2 = plt.twinx()
            plt2.plot(self.data['MR_Signal'], 'go', markersize=1)
            plt.title('Mean Reversion')
            plt.ylabel('Left - Value; Right - mean reversion')
            plt.show()

    def macd(self, show=False):
        for idx, item in self.data.iterrows():
            try:
                if self.data.loc[idx - 1, 'MACD'] < 0 and self.data.loc[idx, 'MACD'] > 0 \
                    or self.data.loc[idx - 1, 'MACD'] - self.data.loc[idx - 2, 'MACD'] < 0 and self.data.loc[idx, 'MACD'] - self.data.loc[idx - 1, 'MACD'] > 0:
                    self.data.loc[idx, 'MACD_Buy'] = True
                else:
                    self.data.loc[idx, 'MACD_Buy'] = False
            except:
                self.data.loc[idx, 'MACD_Buy'] = None
            try:
                if self.data.loc[idx - 1, 'MACD'] > 0 and self.data.loc[idx, 'MACD'] < 0 \
                    or self.data.loc[idx - 1, 'MACD'] - self.data.loc[idx - 2, 'MACD'] > 0 and self.data.loc[idx, 'MACD'] - self.data.loc[idx - 1, 'MACD'] < 0:
                    self.data.loc[idx, 'MACD_Sell'] = True
                else:
                    self.data.loc[idx, 'MACD_Sell'] = False
            except:
                self.data.loc[idx, 'MACD_Sell'] = None
        print(self.data)
        if show == True:
            self.data[['value']].plot(figsize=(12,6))
            plt2 = plt.twinx()
            plt2.plot(self.data['MACD'], 'g--')
            plt2.plot(self.data['MACD_Buy'], 'bo', markersize=1)
            plt2.plot(self.data['MACD_Sell'], 'ro', markersize=1)
            plt.title('MACD')
            plt.ylabel('Left - Value; Right - red=sell, blue=buy, green=macd')
            plt.show()
    
    def kdj(self):
        pass # Needs a full daily Hi/Lo values
    
    def ma(self, show=False):
        for idx, item in self.data.iterrows():
            try:
                self.data.loc[idx, 'MA_Sell'] = (self.data.loc[idx, '100MA'] - self.data.loc[idx, '20MA'] > 0 and self.data.loc[idx-1, '100MA'] - self.data.loc[idx-1, '20MA'] < 0)
                self.data.loc[idx, 'MA_Buy'] = (self.data.loc[idx, '100MA'] - self.data.loc[idx, '20MA'] < 0 and self.data.loc[idx-1, '100MA'] - self.data.loc[idx-1, '20MA'] > 0)
            except:
                self.data.loc[idx, 'MA_Buy'] = None
                self.data.loc[idx, 'MA_Sell'] = None
        if show == True:
            self.data[['value', '20MA', '100MA']].plot(figsize=(12,6))
            plt2 = plt.twinx()
            plt2.plot(self.data['MA_Buy'], 'bo', markersize=1)
            plt2.plot(self.data['MA_Sell'], 'ro', markersize=1)
            plt.title('MA')
            plt.ylabel('Left - Value; Right - red=sell, blue=buy')
            plt.show()

    def rsi(self, window=14, show=False):
        for idx, item in self.data.iterrows():
            try:
                self.data.loc[idx, 'Gain'] = self.data.loc[idx, 'value'] - self.data.loc[idx - 1, 'value'] if self.data.loc[idx, 'value'] - self.data.loc[idx - 1, 'value'] > 0 else 0
                self.data.loc[idx, 'Loss'] = self.data.loc[idx, 'value'] - self.data.loc[idx - 1, 'value'] if self.data.loc[idx, 'value'] - self.data.loc[idx - 1, 'value'] < 0 else 0
            except:
                self.data.loc[idx, 'Gain'] = 0
                self.data.loc[idx, 'Loss'] = 0
            self.data['GainEMA'] = self.data['Gain'].ewm(span=window).mean()
            self.data['LossEMA'] = self.data['Loss'].abs().ewm(span=window).mean()
            self.data.loc[idx, 'RSI'] = 1 - (1 / (1.0 + (self.data.loc[idx, 'GainEMA']/self.data.loc[idx, 'LossEMA'])))
            self.data.loc[idx, 'RSI_Buy'] = True if self.data.loc[idx, 'RSI'] < 0.30 else None
            self.data.loc[idx, 'RSI_Sell'] = True if self.data.loc[idx, 'RSI'] > 0.70 else None
        if show == True:
            self.data[['value']].plot(figsize=(12,6))
            plt2 = plt.twinx()
            plt2.plot(self.data['RSI'], 'g-', markersize=1)
            plt2.plot(self.data['RSI_Buy'], 'bo', markersize=1)           
            plt2.plot(self.data['RSI_Sell'], 'ro', markersize=1)
            plt.title('RSI/100')
            plt.ylabel('Left - Value; Right - red=sell, blue=buy')
            plt.show()

def main():
    filename = "./data/predict-0027.HK.csv"
    x = Indicator(filename)
    #x.bollinger(True)
    #x.mean_reversion(0.09, True)
    #x.macd(True)
    #x.ma(True)
    x.rsi(14, True)


main()