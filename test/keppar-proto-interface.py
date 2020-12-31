import pandas as pd
from indikeppar import Indikeppar
import matplotlib.pyplot as plt
import datetime
from manualkeppar import KepparExecute

class KepparInterface:
    def __init__(self, equity_1, equity_2, init_asset, commission, limit, simulation_limit):
        indicator = Indikeppar(equity_1, equity_2, limit)
        indicator.keppar(term=40,ti=39)
        self.data = indicator.getOutData()
        self.executor = KepparExecute(self.data, init_asset, commission, 60, False)
        self.simulation_limit = simulation_limit

    def run(self):
        self.executor.run_simulator(self.simulation_limit)

def main():
    limit = 600
    simulation_limit = 80
    init_asset = 1000000
    commission = 0.01
    
    equity_1 = "./data/Equities_2282.csv"
    equity_2 = "./data/Equities_27_raw.csv"
    
    k = KepparInterface(equity_1,equity_2,init_asset,commission,limit,simulation_limit)
    k.run()

if __name__ == '__main__':
    main()