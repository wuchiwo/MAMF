import datetime
import backtrader as bt
from indikeppar import *
import csv
import numpy as np

# DEBUG CLASS
class PrintClose(bt.Strategy):

    def __init__(self):
        #Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def log(self, txt, dt=None):
        dt = self.datas[0].datetime.date(0).strftime('%Y.%m.%d %H:%M:%S') + ' ' + str(dt)
        print(txt, dt) #Print date and close

    def next(self):
        self.log('Close: ', self.dataclose[0])

# Example Strat
class MAcrossover(bt.Strategy): 
    # Moving average parameters
    pfast = 20
    pslow = 50

    def next(self):
        # Check for open orders
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for a signal to OPEN trades
                
            #If the 20 SMA is above the 50 SMA
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                self.log(f'BUY CREATE {self.dataclose[0]:2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
            #Otherwise if the 20 SMA is below the 50 SMA   
            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                self.log(f'SELL CREATE {self.dataclose[0]:2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
        else:
            # We are already in the market, look for a signal to CLOSE trades
            if len(self) >= (self.bar_executed + 5):
                self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.order = self.close()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}') # Comment this line when running optimization

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        
        # Order variable will contain ongoing order details/status
        self.order = None

        # Instantiate moving averages
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.pfast)

class KepparStrat(bt.Strategy):
    # TO DO
    pass

# Instantiate Cerebro engine
cerebro = bt.Cerebro()

# Set data parameters and add to Cerebro
limit_data = 2000
path = "data/Equities_27.csv"

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

def loadStockData(path,out_path):
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
    
    stock.to_csv(out_path)
    addTimeHeader(out_path)

loadStockData(removeBreakTimes(path),'temp.csv')


# settings for out-of-sample data
# fromdate=datetime.datetime(2018, 1, 1),
# todate=datetime.datetime(2019, 12, 25))

data = bt.feeds.GenericCSVData(
    dataname='temp.csv',
    nullvalue=0.0,
    datetime=0,
    high=1,
    low=2,
    open=3,
    close=5,
    volume=6,
    openinterest=-1
)

cerebro.adddata(data)

# Add strategy to Cerebro
cerebro.addstrategy(MAcrossover)

# Default position size
cerebro.addsizer(bt.sizers.SizerFix, stake=3)

if __name__ == '__main__':
    # Run Cerebro Engine
    start_portfolio_value = cerebro.broker.getvalue()

    cerebro.run()

    end_portfolio_value = cerebro.broker.getvalue()
    pnl = end_portfolio_value - start_portfolio_value
    print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
    print(f'Final Portfolio Value: {end_portfolio_value:2f}')
    print(f'PnL: {pnl:.2f}')
