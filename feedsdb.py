import pandas as pd
import sqlite3

df = pd.read_csv('feeds-clients-modified.csv')

#conn = sqlite3.connect('feeds-clients.sqlite')
#df.to_sql('feeds-clients', conn, if_exists='replace')

mbo = df[df['MBL'] > 0]
print(mbo.head(10))
