stock = '0027.HK'
data_file = 'data/' + stock + '.csv'
model_file = 'lstm/model/' + stock + '.model'

feature_keys = [
    'Open',
    'High',
    'Low',
    'Close',
    'Adj Close',
    'Volume',
]

predict_key = 'Open'
date_key = 'Date'

split_fraction = 0.715
lookback = 60
epochs = 100
batch_size = 32