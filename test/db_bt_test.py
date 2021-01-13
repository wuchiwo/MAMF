from datetime import datetime, time
from datetime import timedelta
import datetime
from util.data import data_preprocessing
import pandas as pd
import numpy as np
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])
import glob
from testBasic import removeBreakTimes, addTimeHeader, loadStockData
from backtrader.feeds import PandasData  # 用于扩展DataFeed

from numpy import nan, ndarray, ones_like, vstack, random
from numpy.lib.stride_tricks import as_strided
from numpy.linalg import pinv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))
import data as dt

class stampDutyCommissionScheme(bt.CommInfoBase):
    '''
    本佣金模式下，买入股票仅支付佣金，卖出股票支付佣金和印花税.    
    '''
    params = (
        ('stamp_duty', 0.001),  # 印花税率
        ('commission', 160),  # 佣金率
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_PERC),
    )

    def _getcommission(self, size, price, pseudoexec):
        '''
        If size is greater than 0, this indicates a long / buying of shares.
        If size is less than 0, it idicates a short / selling of shares.
        '''

        if size > 0:  # buy
            return size * price + self.p.commission
        elif size < 0:  # sell
            return size * price * self.p.stamp_duty + self.p.commission
        else:
            return 0  # just in case for some reason the size is 0.


class downside_beta_strategy(bt.Strategy):
    # 策略参数
    params = dict(
        printlog=True,
        board_size=500, # batch size of shares. (HK Stock is trade by batch)
        when=bt.timer.SESSION_START,
        timer=True,
        cheat=False,
        offset=datetime.timedelta(),
        repeat=datetime.timedelta(minutes=15),
        weekdays=[],
        weekcarry=False,
        monthdays=[],
        monthcarry=True
    )

    def __init__(self):
        # self.beta_diff = self.datas[0].Beta_Diff
        self.lastRanks = []  # 上次交易股票的列表
        self.stocks = self.datas[1:]
        self.order_list = []
    
    # def notify_timer(self, timer, when, *args, **kwargs):
        # self.rebalance_portfolio()  # 执行再平衡

    def next(self):
        # print('Next: ', self.datas[0])
        # print(self.datas[0].tick_Beta_Diff)
        # pass if it is end of index.
        if len(self.datas[0]) == self.data0.buflen():
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
    
        # get long/short by Beta_Diff.

        if long_stock == short_stock:
            pass

        # All-in and All out
        # Short current stock first
        # check if last 
        if self.getposition(self.datas[short_stock]).size > 0:
            # print('sell ', short_stock._name,
            #       self.getposition(short_stock).size)
            self.order = self.sell(data=self.datas[short_stock], size=self.getposition(self.datas[short_stock]).size)


        # 得到当前的账户价值
        total_value = self.broker.get_cash() * 0.98
        #获取仓位
        price = self.datas[long_stock][0]
        target_size = round(total_value / (price * 1.02), 0)
        buy_total = price * target_size
        # print('buy ', long_stock._name, target_size * self.p.board_size)
        if total_value > buy_total * 1.02 : 
            self.order=self.buy(data=self.datas[long_stock], size=target_size)

    def log(self, txt, dt=None,doprint=False):
        pass
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt},{txt}')

    #记录交易执行情况（可省略，默认不输出结果）
    def notify_order(self, order):
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
            self.log('Transaction failed. Status: ', order.Status[order.status], order.ordtype)
        self.order = None

    #记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self,trade):
        if not trade.isclosed:
            return
        # self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')



cerebro = bt.Cerebro(stdstats=False)
cerebro.addobserver(bt.observers.Broker)
cerebro.addobserver(bt.observers.Trades)

datadir = '../data/raw'
datafilelist = glob.glob(os.path.join(datadir, '*'))  # 数据文件路径列表

maxstocknum = 6
datafilelist = datafilelist[0:maxstocknum]  # 截取指定数量的股票池
print(datafilelist)
# Data preprocess
stocks = ['27', '200', '880', '2282']


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
        ('close', 1),
        ('volume', 2),
        ('Beta_Diff', 8),
    )    # Add a 'pe' line to the inherited ones from the base class

for stock in stocks:
    print(stock)
    # path = removeBreakTimes(stock)
    # Load your stock data through this function
    # The data must contain value of 'Open','High','Low','Close', although you may not use it for strategy
    # stockData = loadStockData(path)
    # print(stockData['Open'].items())
    # stockData['Last Trade'] = stockData['Open']
    # data = pd.read_csv(stockData)
   
    data = OandaCSVData(dataname='data/train/Equities_%s.csv' % stock, Beta_Diff=10)
    cerebro.adddata(data, name=stock)

cerebro.addstrategy(downside_beta_strategy)
startcash = 10000000
cerebro.broker.setcash(startcash)
# 防止下单时现金不够被拒绝。只在执行时检查现金够不够。
cerebro.broker.set_checksubmit(False)
comminfo = stampDutyCommissionScheme()
cerebro.broker.addcommissioninfo(comminfo)
results = cerebro.run()
print('Net Total price: %.2f' % cerebro.broker.getvalue())
print('Final Profit: %.2f %%' % (int(cerebro.broker.getvalue()-startcash) / startcash * 100))
# cerebro.plot() 
