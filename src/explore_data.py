import pandas as pd

df1 = pd.read_csv('data/malicious_phish.csv')
df2 = pd.read_csv('data/malicious_phish2.csv')
lf1 = pd.read_csv('data/legit_sites.csv')

df1 = df1.drop_duplicates().dropna(subset=['url'])
df2 = df2.drop_duplicates().dropna(subset=['url'])
lf1 = lf1.drop_duplicates().dropna(subset=['url'])

df1 = df1[['url','type']].copy()

df2 = df2[['url']].copy
df2.clean['type'] = 'phishing'