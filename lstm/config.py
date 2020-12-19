stock = 'Equities_27'
data_file = './data/' + stock +'.csv'
predict_file = './predict/' + stock + '.csv'
model_dir = './lstm/model/' + stock + '/'

feature_keys = [
    'Last Trade',
    'Volume',
    'MA5',
    'MA10',
    'MA20',
    'VOL'
]

colors = [
    "blue",
    "orange",
    "green",
    "red",
    "purple",
    "brown",
    "pink",
    "gray",
    "olive",
    "cyan",
]   

predict_key = 'Last Trade'
date_key = 'Time'
date_format = '%Y/%m/%d %H:%M'

split_fraction = 0.85
past = 798
future = 60
epochs = 100 #100 #500
batch_size = 512