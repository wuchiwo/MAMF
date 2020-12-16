import pandas as pd
import matplotlib.pyplot as plt
import math

class Indikeppar:
    def __init__(self, equity_1_file, equity_2_file, limit=0):
        self.e1_data = pd.read_csv(equity_1_file)
        self.e2_data = pd.read_csv(equity_2_file)
        # Limit input to limit
        if limit != 0:
            self.e1_data = self.e1_data[-limit:]
            self.e2_data = self.e2_data[-limit:]

    def calculateP(self, type, idx, T):
        P = 1
        if type == 'A':
            for i in range(T+1):
                P *= (1 + self.e1_data.loc[idx - i, 'R'])
        else:
            for i in range(T+1):
                P *= (1 + self.e2_data.loc[idx - i, 'R'])
        return math.log(P)

    def calculateS(self, idx, T):
        S = self.calculateP('A', idx, T) - self.calculateP('B', idx, T)
        return S

    def calculateMiu(self, idx, t, T):
        miu = 0
        for i in range(t, T+1):
            miu += self.calculateS(idx, i) / (T-t+1)
        return miu

    def calculateSigma(self, idx, t, T):
        miu = self.calculateMiu(idx, t, T)
        sigma = 0
        for i in range(t, T+1):
            sigma += (self.calculateS(idx, i) - miu) / (T-t+1)
        return sigma

    def calculateTtest(self, idx, t, T):
        self.e1_data.loc[idx, 'tTest'] = (self.calculateS(idx, T) - self.calculateMiu(idx, t, T)) \
                                      / self.calculateSigma(idx, t, T)

    def calculateKeppar(self, idx, t, T):
        self.e1_data.loc[idx, 'keppar'] = self.calculateMiu(idx, t, T) / self.calculateMiu(idx, t-1, T-1) - 1

    def loadDailyReturn(self):
        for idx, item in self.e1_data.iterrows():
            try:
                self.e1_data.loc[idx, 'R'] = self.e1_data.loc[idx, 'Last Trade'] - self.e1_data.loc[idx-1, 'Last Trade']
            except:
                pass

        for idx, item in self.e2_data.iterrows():
            try:
                self.e2_data.loc[idx, 'R'] = self.e2_data.loc[idx, 'Last Trade'] \
                                                     - self.e2_data.loc[idx-1, 'Last Trade']
            except:
                pass

    def keppar(self, term=10, ti=5, draw=False):
        self.loadDailyReturn()

        for idx, item in self.e1_data.iterrows():
            try:
                self.calculateTtest(idx, ti, term)
                self.calculateKeppar(idx, ti, term)
            except:
                pass


        for idx, item in self.e1_data.iterrows():
            self.e1_data.loc[idx, 'keppar_Enable'] = -0.3 < self.e1_data.loc[idx, 'keppar'] and 0.3 > self.e1_data.loc[
                idx, 'keppar']
            self.e1_data.loc[idx, 'keppar_Buy_A'] = (self.e1_data.loc[idx, 'tTest'] > 1.8) * self.e1_data.loc[idx, 'keppar_Enable']
            self.e1_data.loc[idx, 'keppar_Sell_A'] = (self.e1_data.loc[idx, 'tTest'] < 1.8) * self.e1_data.loc[idx, 'keppar_Enable']
            self.e1_data.loc[idx, 'keppar_Close'] = ((self.e1_data.loc[idx, 'tTest'] < 0 and self.e1_data.loc[
                                                     idx - 1, 'tTest'] > 0) or \
                                                 (self.e1_data.loc[idx, 'tTest'] > 3 and self.e1_data.loc[
                                                     idx - 1, 'tTest'] < 3) or \
                                                 (self.e1_data.loc[idx, 'tTest'] < -3 and self.e1_data.loc[
                                                     idx - 1, 'tTest'] > -3)) * self.e1_data.loc[idx, 'keppar_Enable']
            self.e2_data.loc[idx, 'keppar_Buy_B'] = (self.e1_data.loc[idx, 'tTest'] < 1.8) * self.e1_data.loc[idx, 'keppar_Enable']
            self.e2_data.loc[idx, 'keppar_Sell_B'] = (self.e1_data.loc[idx, 'tTest'] > 1.8) * self.e1_data.loc[idx, 'keppar_Enable']      

        if draw == True:
            self.e1_data[['Last Trade']].plot(figsize=(12, 6))
            plt2 = plt.twinx()
            plt2.set_ylim(-10, 10)
            plt2.plot(self.e1_data['keppar'], 'y-', markersize=1)
            plt2.plot(self.e1_data['tTest'], 'g-', markersize=1)
            plt2.plot(self.e1_data['keppar_Buy_A'], 'bo', markersize=1)
            plt2.plot(self.e1_data['keppar_Sell_A'], 'ro', markersize=1)
            plt2.plot(self.e2_data['keppar_Buy_B'] * 1.1, 'bo', markersize=1) # will be shown slightly over A
            plt2.plot(self.e2_data['keppar_Sell_B'] * 1.1, 'ro', markersize=1) # will be shown slightly over A
            plt2.plot(self.e1_data['keppar_Close'] * -0.1, 'yo', markersize=1) # will be shown slightly below no-signal
            plt.title('Keppar')
            plt.ylabel('Left - Value; Right - Buy = blue, Sell = red')
            plt.show()

def main():
    lim = 2000
    equity_1 = "./data/Equities_200.csv"
    equity_2 = "./data/Equities_27.csv"
    x2 = Indikeppar(equity_1, equity_2, limit=lim)
    x2.keppar(draw=True)

if __name__ == '__main__':
    main()