import backtrader as bt
import util.data as dta
from datetime import datetime

class BetaStrategy(bt.Strategy):

    params = (
        ('sma1', 40),
        ('sma2', 200),
        ('oneplot', True)
    )
    
    def __init__(self):
        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d]['sma1'] = bt.indicators.SimpleMovingAverage(
                d.close, period=self.params.sma1)
            self.inds[d]['sma2'] = bt.indicators.SimpleMovingAverage(
                d.close, period=self.params.sma2)
            self.inds[d]['cross'] = bt.indicators.CrossOver(self.inds[d]['sma1'],self.inds[d]['sma2'])

            if i > 0: #Check we are not on the first loop of data feed:
                if self.p.oneplot == True:
                    d.plotinfo.plotmaster = self.datas[0]

    def next(self):
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name
            pos = self.getposition(d).size
            if not pos:  # no market / no orders
                if self.inds[d]['cross'][0] == 1:
                    self.buy(data=d, size=1000)
                elif self.inds[d]['cross'][0] == -1:
                    self.sell(data=d, size=1000)
            else:
                if self.inds[d]['cross'][0] == 1:
                    self.close(data=d)
                    self.buy(data=d, size=1000)
                elif self.inds[d]['cross'][0] == -1:
                    self.close(data=d)
                    self.sell(data=d, size=1000)

    def notify_trade(self, trade):
        dt = self.data.datetime.date()
        if trade.isclosed:
            print('{} {} Closed: PnL Gross {}, Net {}'.format(
                                                dt,
                                                trade.data._name,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))

class OandaCSVData(bt.feeds.GenericCSVData):
    params = (
        ('nullvalue', float('NaN')),
        ('dtformat', '%Y/%m/%d %H:%M'),
        ('datetime', 0),
        ('time', -1),
        ('open', 1),
        ('high', 1),
        ('low', 1),
        ('close', 1),
        ('volume', 2),
        ('openinterest', -1),
    )

if __name__ == '__main__':
    stocks = ['27', '200', '880', '2282']
    startcash = 10000
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(BetaStrategy)
    for stock in stocks:
        data = OandaCSVData(dataname='data/train/Equities_%s.csv' % stock)
        cerebro.adddata(data, name=stock)
    cerebro.run()

    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))

# class BetaStrategy(Strategy):
    
#     def init(self):
#         self.beta = dta.read_data('data/raw/beta.csv')

#     def next(self):
#         rsi =  self.data['RSI'][-1]
#         price = self.data['Last Trade'][-1]
#         max_beta = self.beta[-1][1:].max(axis=1)
#         min_beta = self.beta[-1][1:].min(axis=1)

#         if (not self.position and rsi > 70):
#             self.buy(sl=.92 * price)
#         elif rsi < 30:
#             self.position.close()

# if __name__ == '__main__':
#     data = dta.read_data('data/raw/Equities_27.csv')
#     bt = Backtest(data, BetaStrategy, commission=.002,
#                 exclusive_orders=True)
#     stats = bt.run()
#     bt.plot()