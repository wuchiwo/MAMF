import pandas as pd
import numpy as np
from scipy import stats

class StockFeatures(object):
    """
    docstring
    """
    @staticmethod
    def getSMA10(df:pd.DataFrame):
        """
        params: 
            df: pandas.DataFrame
            A DataFrame object contains df basic data: Date, open price
        """
        df['SMA10'] = df['Last Trade'].rolling(
            window=10).mean().fillna(0)
        return df
    
    @staticmethod
    def funcname(self, parameter_list):
        """
        docstring
        """
        pass


if __name__ == "__main__":
    stock = pd.read_csv("../data/Equities_27.csv")
    df = StockFeatures.getSMA10(stock)
    print(df)

    
