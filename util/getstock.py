import yfinance as yf
import os
import os.path

def savestock(stockcode):
    stock = yf.Ticker(stockcode)
    stock.history(period="max")
    stock.to_csv("../data/"+stockcode+".csv")


def saveOptions(stockcode) :
    stock = yf.Ticker(stockcode)
    stock.history(period="max")
    opts = stock.options
    for opt in opts:
        calls = stock.option_chain(opt).calls
        calls.to_csv("../data/"+stockcode+"/"+stockcode +
                     '_call_'+opt+'.csv', mode='a+')

# test code
def test():
    dir = os.path.join("../data", "TSLA")
    if not os.path.exists(dir):
        os.mkdir(dir)
    saveOptions("TSLA")
