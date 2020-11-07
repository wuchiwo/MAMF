import keras.models as md
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

import config as c

df = pd.read_csv(c.data_file)
model = md.load_model(c.model_file)
sc = MinMaxScaler(feature_range=(0, 1))

dataset_train = df.iloc[:c.train_size, c.train_columns]
dataset_test = df.iloc[c.train_size:, c.train_columns]
dataset_total = pd.concat((dataset_train, dataset_test))

print(dataset_test.shape)
inputs = dataset_total[len(dataset_total) -
                       len(dataset_test) - c.lookback:].values
                       
inputs = sc.fit_transform(inputs)

x_test = []
for i in range(c.lookback, inputs.shape[0]):
    x_test.append(inputs[i-c.lookback:i])
x_test = np.array(x_test)

print(x_test.shape)
predicted_stock_price = model.predict(x_test)
print(predicted_stock_price.shape)
predicted_stock_price = sc.inverse_transform(predicted_stock_price)

plt.plot(df.loc[c.train_size:, 'Date'], dataset_test.values,
         color='red', label='Real ' + c.stock + ' Stock Price')
plt.plot(df.loc[c.train_size:, 'Date'], predicted_stock_price,
         color='blue', label='Predicted ' + c.stock + ' Stock Price')
plt.xticks(np.arange(0, 459, 50))
plt.title(c.stock + ' Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel(c.stock + ' Stock Price')
plt.legend()
plt.show()
