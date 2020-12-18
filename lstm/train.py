import numpy as np
import pandas as pd
from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import tensorflow as tf
import lstm.config as cfg

for gpu in  tf.config.experimental.list_physical_devices('GPU'):
    tf.config.experimental.set_memory_growth(gpu, True)

df = pd.read_csv(cfg.data_file)
sc = MinMaxScaler(feature_range=(0, 1))

train_size = int(cfg.split_fraction * int(df.shape[0]))
train_set = df.loc[:train_size - 1, cfg.feature_keys].values
train_set_scaled = sc.fit_transform(train_set)
predict_key_index = df.columns.get_loc(cfg.predict_key) - 1

x_train = []
y_train = []

for i in range(cfg.past, train_set_scaled.shape[0] - cfg.future):
    x_train.append(train_set_scaled[i-cfg.past:i])
    y_train.append(
        train_set_scaled[i + cfg.future, predict_key_index])

x_train, y_train = np.array(x_train), np.array(y_train)

model = Sequential()
model.add(LSTM(units=50, return_sequences=True,
               input_shape=(x_train.shape[1], x_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50))
model.add(Dropout(0.2))
model.add(Dense(units=1))
model.compile(optimizer='adam', loss='mean_squared_error')
history = model.fit(x_train, y_train, epochs=cfg.epochs, batch_size=cfg.batch_size, validation_split=0.18)
model.save(cfg.model_dir)

loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(loss) + 1)

# plt.figure()
# plt.plot(epochs, loss, 'bo', label='Training loss')
# plt.plot(epochs, val_loss, 'b', label='Validation loss')
# plt.title('Training and validation loss')
# plt.legend()
# plt.show()
