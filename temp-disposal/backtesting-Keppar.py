import datetime
import backtrader as bt
from indikeppar import *
import csv
import numpy as np

class KepparStrat(bt.Strategy):
    params = (("printlog", True), ("quantity", 200))

    def log(self, txt, dt=None, doprint=False):
        """Logging function for strategy"""
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f"{dt.isoformat()}, {txt}")

    def __init__(self):
        self.position_type = None  # long or short
        self.quantity = self.params.quantity

    def next(self):
        if self.position:
            if self.position_type == "long" and e > -sqrt_Q:
                self.close(self.data0)
                self.close(self.data1)
                self.position_type = None
            if self.position_type == "short" and e < sqrt_Q:
                self.close(self.data0)
                self.close(self.data1)
                self.position_type = None

        else:
            if e < -sqrt_Q:
                self.sell(data=self.data0, size=(self.quantity * self.beta[0]))
                self.buy(data=self.data1, size=self.quantity)

                self.position_type = "long"
            if e > sqrt_Q:
                self.buy(data=self.data0, size=(self.quantity * self.beta[0]))
                self.sell(data=self.data1, size=self.quantity)
                self.position_type = "short"

        self.log(f"beta: {self.beta[0]}, alpha: {self.beta[1]}")

def run():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(KepparStrat)
   
    startdate = datetime.datetime(2015, 1, 1)
    enddate = datetime.datetime(2017, 1, 1)

    ewa = bt.feeds.YahooFinanceData(dataname="0027.HK", fromdate=startdate, todate=enddate)
    ewc = bt.feeds.YahooFinanceData(dataname="0880.HK", fromdate=startdate, todate=enddate)

    cerebro.adddata(ewa)
    cerebro.adddata(ewc)

    cerebro.broker.setcommission(commission=0.0001)
    cerebro.broker.setcash(1000000.0)

    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    cerebro.run()
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
    cerebro.plot()


if __name__ == "__main__":
    run()

'''
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
'''