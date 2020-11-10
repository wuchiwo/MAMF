import keras.models as md
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

import config as c

df = pd.read_csv(c.data_file)
model = md.load_model(c.model_file)
sc = MinMaxScaler(feature_range=(0, 1))

train_size = int(c.split_fraction * int(df.shape[0]))
predict_key_index = df.columns.get_loc(c.predict_key) - 1

train_set = df.loc[:train_size, c.feature_keys]
test_set = df.loc[train_size:, c.feature_keys]
total_set = pd.concat((train_set, test_set))

inputs = total_set[len(train_set) - c.lookback:].values
inputs = sc.fit_transform(inputs)

x_test = []
for i in range(c.lookback, inputs.shape[0]):
    x_test.append(inputs[i-c.lookback:i])
x_test = np.array(x_test)

predict_value_scaled = model.predict(x_test)
temp_set = np.zeros(shape=(len(predict_value_scaled), len(c.feature_keys)))
temp_set[:, predict_key_index] = predict_value_scaled[:, predict_key_index]
predict_value = sc.inverse_transform(temp_set)[:, predict_key_index]

plt.plot(df.loc[train_size:, c.date_key], test_set.values[:, predict_key_index],
         color='red', label='Real ' + c.stock + ' ' + c.predict_key)
plt.plot(df.loc[train_size:, c.date_key], predict_value,
         color='blue', label='Predicted ' + c.stock+ ' ' + c.predict_key)
plt.xticks(np.arange(0, 459, 50))
plt.title(c.stock + ' ' + c.predict_key + ' Prediction')
plt.xlabel('Time')
plt.ylabel(c.stock + ' ' + c.predict_key )
plt.legend()
plt.show()

# Save to .csv for further uses
f = open("./data/predict-"+c.stock+".csv", "w")
dates = []
f.write('time,value\n')
for entry in (df.values.tolist()):
    dates.append(entry[0])

for i in range(train_size):
    f.write(dates[i] + ',' + str(total_set.values.tolist()[i][4]) + '\n')

for i in range(len(predict_value)):
    f.write(dates[i+train_size] + ',' + str(predict_value[i]) + '\n')
f.close()
