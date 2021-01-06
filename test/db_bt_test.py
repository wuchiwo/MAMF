from datetime import datetime, time
from datetime import timedelta
import datetime
import pandas as pd
import numpy as np
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])
import glob
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
        self.beta_diffs = dict()
        self.lastRanks = []  # 上次交易股票的列表
        self.stocks = self.datas[1:]
        self.order_list = []
    
    def notify_timer(self, timer, when, *args, **kwargs):
        self.rebalance_portfolio()  # 执行再平衡

    def rebalance_portfolio(self):
        print('Next: ', self.datas[0])
        # pass if it is end of index.
        if len(self.datas[0]) == self.data0.buflen():
            return     

        # 取消以往所下订单（已成交的不会起作用）
        for o in self.order_list:
            self.cancel(o)
        self.order_list = []  # 重置订单列表
        
        # Rank those 6 stocks by beta diff
        self.ranks = [d for d in self.stocks if
                      len(d) > 0  
                      ]

        # get long/short by beta diff.
        short_stock = min(r['Beta Diff'] for r in self.datas)
        long_stock  = max(r['Beta Diff'] for r in self.datas)

        if  len(long_stock) > 1 or len(short_stock) > 1 :
            return # hold if multiple stock hits the criteria

        # All-in and All out
        # Short current stock first
        # check if last 
        print('sell ', short_stock[0]._name, self.getposition(short_stock[0]).size)
        o = self.close(data=short_stock[0])            
        self.order_list.append(o) # log the order
        
        # save 2 % cash for commissions and trading fee.
        target_price = 0.98 * self.broker.getvalue()

        # 得到当前的账户价值
        total_value = self.broker.getvalue()
            #获取仓位
        pos = self.getposition(data).size
        target_size = total_value * 0.98 / (pos * 1.12) / self.p.board_size
        print('buy ', long_stock[0]._name, self.getposition(short_stock[0]).size)
        o = self.buy(data=long_stock[0], size=target_size * self.p.board_size, price=pos*1.12)            
        self.order_list.append(o) # log the order
        # if not pos and data._name in long_stock and \
        #     self.mas[data._name][0]>data.close[0]:
        #     size=int(p_value/100/data.close[0])*100
        #     self.buy(data = data, size = size) 

        # if pos!=0 and data._name not in long_stock or \
        #     self.mas[data._name][0]<data.close[0]:
        #     self.close(data = data)                        

    def log(self, txt, dt=None,doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

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
            self.log('Transaction failed')
        self.order = None

    #记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self,trade):
        pass
        # if not trade.isclosed:
        #     return
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
for fname in datafilelist:
    print(fname)
    if fname.find('mei'):
        continue
    # data = bt.feeds.GenericCSVData(dataname=fname, datetime=0, open=1, volume=2, kwargs = dict(
    #     timeframe=bt.TimeFrame.Minutes,
    #     compression=5,
    #     sessionstart=datetime.time(9, 0),
    #     sessionend=datetime.time(17, 30),
    # ))
    data = bt.feeds.GenericCSVData(
            dataname=fname,
            datetime=0,
            fromdate=datetime.datetime(2020, 9, 24),
            timeframe=bt.TimeFrame.Minutes,
            dtformat=('%d-%m-%Y %H:%M'),
            open=1,
            high=-1,
            low=-1,
            close=-1,
            volume=2,
            openinterest=-1)
    print(data.tail(20))
    data = dt.data_preprocessing(data)
    
    cerebro.adddata(data, name=fname[11:-4])

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
