import backtrader as bt
from backtrader import sizer
import util.data as dta
from datetime import datetime
import sys
import pandas as pd


class stampDutyCommissionScheme(bt.CommInfoBase):
    params = (
        ('stamp_duty', 0.001), 
        ('commission', 160),  
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_PERC),
    )

    def _getcommission(self, size, price, pseudoexec):
        if size > 0:  # buy
            return size * price + self.p.commission
        elif size < 0:  # sell
            return size * price * self.p.stamp_duty + self.p.commission
        else:
            return 0  # just in case for some reason the size is 0.


class BetaStrategy(bt.Strategy):

    params = (
        ('printlog', True),
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
            o = self.sell(data=self.datas[short_stock])
        if self.broker.getcash() > self._sizer.p.stake * self.datas[long_stock].open:
            o = self.buy(data=self.datas[long_stock])

    def notify_trade(self, trade: bt.Trade):
        dt = self.data.datetime.date()
        if trade.isclosed:
            print('{} {} Closed: PnL Gross {}, Net {}'.format(
                                                dt,
                                                trade.data._name,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))
        if trade.isopen:
            print('{} {} Open: PnL Gross {}, Net {}'.format(
                dt,
                trade.data._name,
                round(trade.pnl, 2),
                round(trade.pnlcomm, 2)))

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt},{txt}')

    def notify_order(self, order: bt.order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'Buy:\nprice:{order.executed.price:.2f},\
                Cost:{order.executed.value:.2f},\
                Comission:{order.executed.comm:.2f}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'Sell:\nPrice：{order.executed.price:.2f},\
                Cost: {order.executed.value:.2f},\
                Comission{order.executed.comm:.2f}')

            self.bar_executed = len(self)

        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            pass
            # self.log('Transaction failed. Status: %s',
            #          order.Status[order.status])
        self.order = None


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
    import sys
    sys.stdout = open('Beta_test.txt', 'w')
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
    # comminfo = stampDutyCommissionScheme()
    # cerebro.broker.addcommissioninfo(comminfo)
    
    cerebro.addwriter(bt.WriterFile, out='downside_beta_test.txt')
    cerebro.run()

    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))
    profit_rate = (pnl/startcash)*100
    print('Increment: {} %'.format(profit_rate))
    figure = cerebro.plot(style='candlebars')[0][0]
    figure.savefig('downside_beta_test.png')
