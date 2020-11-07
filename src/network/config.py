stock = '0027.HK'
data_file = 'data/' + stock + '.csv'
model_file = 'model/' + stock + '.model'

train_columns = slice(1, 7)
predict_column = 1

train_size = 800

lookback = 60
epochs = 100
batch_size = 32