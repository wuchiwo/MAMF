import pandas as pd
import lstm.config as cfg

df = pd.read_csv(cfg.data_file)
df['MA5'] = df['Last Trade'].rolling(window=5).mean().fillna(0)
df['MA10'] = df['Last Trade'].rolling(window=10).mean().fillna(0)
df['MA20'] = df['Last Trade'].rolling(window=20).mean().fillna(0)
df['VOL'] = df['Last Trade'].rolling(window=10).std().fillna(0)
df.to_csv(path_or_buf=cfg.data_file, index=False)



