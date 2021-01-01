from backtesting import Backtest, Strategy
from backtesting.lib import crossover

import util.data as dta

class BetaStrategy(Strategy):
    
    def init(self):
        self.stock = '20'

    def next(self):
        rsi =  self.data['RSI'][-1]
        price = self.data['Last Trade'][-1]
        time = self.data['Time'][-1]
        dta.get_beta_difference(self.data[-1])

        if (not self.position and rsi > 70):
            self.buy(sl=.92 * price)
        elif rsi < 30:
            self.position.close()

if __name__ == '__main__':
    data = dta.read_data('data/train/Equities_27.csv')
    bt = Backtest(data, BetaStrategy, commission=.002,
                exclusive_orders=True)
    stats = bt.run()
    bt.plot()