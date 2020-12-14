import keras.models as md
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import lstm.config as cfg

for gpu in tf.config.experimental.list_physical_devices('GPU'):
    tf.config.experimental.set_memory_growth(gpu, True)

df = pd.read_csv(cfg.data_file)
model = md.load_model(cfg.model_dir)
sc = MinMaxScaler(feature_range=(0, 1))

train_size = int(cfg.split_fraction * int(df.shape[0]))
predict_key_index = df.columns.get_loc(cfg.predict_key) - 1

train_set = df.loc[:train_size - 1, cfg.feature_keys]
test_set = df.loc[train_size:, cfg.feature_keys]
total_set = pd.concat((train_set, test_set))

inputs = total_set[len(train_set) - cfg.future - cfg.past:].values
inputs = sc.fit_transform(inputs)

x_test = []
for i in range(cfg.past, inputs.shape[0] - cfg.future):
    x_test.append(inputs[i-cfg.past:i])
x_test = np.array(x_test)

predict_value_scaled = model.predict(x_test)
temp_set = np.zeros(shape=(len(predict_value_scaled), len(cfg.feature_keys)))
temp_set[:, predict_key_index] = predict_value_scaled[:, predict_key_index]
predict_value = sc.inverse_transform(temp_set)[:, predict_key_index]

new_predict_key = 'Predicted ' + cfg.predict_key
predict_set = pd.DataFrame(columns = [cfg.date_key, cfg.predict_key, new_predict_key])
predict_set[cfg.date_key] = df.loc[train_size:, cfg.date_key]
predict_set[cfg.predict_key] =  test_set.values[:, predict_key_index]
predict_set[new_predict_key] = predict_value
predict_set[new_predict_key] = predict_set[new_predict_key].shift(periods=cfg.future)
predict_set.to_csv(path_or_buf=cfg.predict_file, index=False)

plt.plot(predict_set[cfg.date_key], predict_set[cfg.predict_key],
         color='red', label='Real ' + cfg.stock + ' ' + cfg.predict_key)
plt.plot(predict_set[cfg.date_key] , predict_set[new_predict_key],
         color='blue', label='Predicted ' + cfg.stock + ' ' + cfg.predict_key)
plt.xticks(np.arange(0, predict_set.shape[0], predict_set.shape[0] / 10), rotation=45)
plt.title(cfg.stock + ' ' + cfg.predict_key + ' Prediction')
plt.xlabel('Time')
plt.ylabel(cfg.stock + ' ' + cfg.predict_key)
plt.legend()
plt.show()
