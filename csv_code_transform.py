import pandas as pd

df = pd.read_csv('data.csv', encoding='utf-8')

# 替换 DataFrame 中的非断空格为普通空格
df = df.replace('\xa0', ' ', regex=True)

df.to_csv('car_price.csv', encoding='cp932', index=False)
