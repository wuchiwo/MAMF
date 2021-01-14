import backtrader as bt
from backtrader import sizer
import util.data as dta
from datetime import datetime

class BetaStrategy(bt.Strategy):

    params = (

    )
    
    def __init__(self):
        pass

    def next(self):

        if len(self.datas[0]) == self.data0.buflen():
            return
        mei_rsi = self.datas[0].close[0]
        if mei_rsi > 70: # MEI_RSI > 70
            return
        long_stock_beta = self.datas[0].tick_Beta_Diff
        long_stock = 0
        short_stock_beta = self.datas[0].tick_Beta_Diff
        short_stock = 0
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name
            if d.tick_Beta_Diff > long_stock_beta:
                long_stock = i
                long_stock_beta = d.tick_Beta_Diff
            if d.tick_Beta_Diff < short_stock_beta:
                short_stock = i
                short_stock_beta = d.tick_Beta_Diff

        if long_stock == short_stock:
            return

        if self.getposition(self.datas[short_stock]).size > 0:
            # print(self.datas[short_stock]._name)
            o = self.sell(data=self.datas[short_stock])

        o = self.buy(data=self.datas[long_stock])
        # print(self.datas[long_stock]._name)
        
        # print(self.broker.getvalue())

    def notify_trade(self, trade):
        dt = self.data.datetime.date()
        if trade.isclosed:
            print('{} {} Closed: PnL Gross {}, Net {}'.format(
                                                dt,
                                                trade.data._name,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))


class OandaCSVData(bt.feeds.GenericCSVData):
    lines = ('Beta_Diff',)
    params = (
        ('nullvalue', float('NaN')),
        ('dtformat', '%Y/%m/%d %H:%M'),
        ('datetime', 0),
        ('time', -1),
        ('open', 1),
        ('high', 1),
        ('low', 1),
        ('close', 9),
        ('volume', 2),
        ('Beta_Diff', 10),
    )    # Add a 'pe' line to the inherited ones from the base class

if __name__ == '__main__':
    stocks = ['27', '200', '880', '2282']
    startcash = 1000000
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(BetaStrategy)

    for stock in stocks:
        data = OandaCSVData(dataname='data/train/Equities_%s.csv' %
                            stock, close=9, Beta_Diff=10)
        cerebro.adddata(data, name=stock)
    print(cerebro.broker.getvalue())
    cerebro.addsizer(sizercls=bt.sizers.FixedSize, stake=2000)
    cerebro.run()

    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))
