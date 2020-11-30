stock = 'Equities_200'
data_file = './data/' + stock +'.csv'
predict_file = './predict/' + stock + '.csv'
model_dir = './lstm/model/' + stock + '/'

feature_keys = [
    'Last Trade',
    'Volume'
]

predict_key = 'Last Trade'
date_key = 'Time'

split_fraction = 0.85
past = 60
future = 3
epochs = 2
batch_size = 512