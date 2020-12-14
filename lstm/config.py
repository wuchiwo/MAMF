stock = 'Equities_27'
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
past = 798
future = 60
epochs = 1 #500
batch_size = 512