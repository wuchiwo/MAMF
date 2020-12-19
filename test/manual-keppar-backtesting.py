import pandas as pd
from indikeppar import Indikeppar
import matplotlib.pyplot as plt
import datetime

class KepparExecute:
    def __init__(self, data, test_limit, init_asset, commission, ignore, log):
        self.test_limit = test_limit
        self.init_asset = init_asset
        self.asset = init_asset
        self.commission = commission
        self.data = data
        self.equities = {'E1' : 0, 'E2' : 0}
        self.ignore = ignore
        self.log = log
    
    def long_(self, idx, equity, size):
        self.equities[equity] += size
        self.asset -= (self.get(idx, equity) * size)

    def short_(self, idx, equity, size):
        self.equities[equity] -= size
        self.asset += (self.get(idx, equity) * size)

    def close_(self, idx, equities):
        for equity in equities:
            size = self.equities[equity]
            self.short_(idx, equity, size)

    def get(self, index, colname):
        return self.data.loc[index, colname]

    def run(self):
        count = 0
        holding_period = 0
        for idx, item in self.data.iterrows():
            count += 1
            if count < self.ignore:
                continue
            #size = min(self.asset/self.get(idx,'E1'),self.asset/self.get(idx,'E2'))
            size = 1000
            if self.get(idx, 'kp_close') or holding_period > 10:
                self.close_(idx, ['E1', 'E2'])
                holding_period = 0
                if self.log:
                    print(self.get(idx, 'Time'), 'CLOSE POSITION')
                    print('    Asset: %7d, E1: %4d, E2: %4d' % (self.asset, self.equities['E1'], self.equities['E2']))
            elif self.get(idx, 'kp_LASB'):
                self.long_(idx, 'E1', size)
                self.short_(idx, 'E2', size)
                holding_period += 1
                if self.log:
                    print(self.get(idx, 'Time'), 'LONG E1@ %3.2f SHORT E2@ %3.2f, size: %3d' % (self.get(idx, 'E1'), self.get(idx, 'E2'), size))
                    print('    Asset: %7d, E1: %4d, E2: %4d' % (self.asset, self.equities['E1'], self.equities['E2']))
            elif self.get(idx, 'kp_SALB'):
                self.short_(idx, 'E1', size)
                self.long_(idx, 'E2', size)
                holding_period += 1
                if self.log:
                    print(self.get(idx, 'Time'), 'SHORT E1@ %3.2f LONG E2@ %3.2f, size: %3d' % (self.get(idx, 'E1'), self.get(idx, 'E2'), size))
                    print('    Asset: %7d, E1: %4d, E2: %4d' % (self.asset, self.equities['E1'], self.equities['E2']))
            self.data.loc[idx,'E1_qty'] = self.equities['E1']
            self.data.loc[idx,'asset'] = self.asset
        self.close_(idx, ['E1', 'E2'])
        print('FINAL ASSET VALUATION:', self.asset)
        print('PROFIT/LOSS          : %3.2f%%' % (100 * self.asset / self.init_asset - 100))

    def draw(self):
        fig, (eq1, hold, value) = plt.subplots(3)
        eq1.set_title('E1 (red-left), E2 (blue-right) price')
        eq1.plot(self.data['E1'], 'r-')
        eq2 = eq1.twinx()
        eq2.plot(self.data['E2'], 'b-')
        hold.set_title('E1 Holding Size (E2 = -E1)')
        hold.plot(self.data['E1_qty'])
        value.set_title('Asset Valuation')
        value.plot(self.data['asset'])        
        plt.show()

def main():
    limit = 120
    ignore_first = 60
    init_asset = 100000
    commission = 0.001
    draw = False

    equity_1 = "./data/Equities_880.csv"
    equity_2 = "./data/Equities_200.csv"
    indicator = Indikeppar(equity_1, equity_2, limit)

    #daily_1 = "temp-disposal/0880.HK.csv"
    #daily_2 = "temp-disposal/0200.HK.csv"
    #indicator = Indikeppar(daily_1, daily_2, limit=0)
    indicator.keppar()
    if draw == True:
        indicator.draw()
    data = indicator.getOutData()
    print(data)

    k = KepparExecute(data, limit, init_asset, commission, ignore_first, log=True)   
    k.run()
    k.draw()

if __name__ == '__main__':
    main()