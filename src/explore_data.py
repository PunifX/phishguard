import pandas as pd

df1 = pd.read_csv('data/malicious_phish.csv')
df2 = pd.read_csv('data/malicious_phish2.csv')
lf1 = pd.read_csv('data/legit_sites.csv')

df1 = df1.drop_duplicates().dropna(subset=['url'])
df2 = df2.drop_duplicates().dropna(subset=['url'])
lf1 = lf1.drop_duplicates().dropna(subset=['url'])

df1 = df1[['url','type']].copy()

df1['type'] = df1['type'].map({
    'benign' : 'benign',
    'phishing': 'phishing',
    'defacement': 'phishing',
    'malware': 'phishing',
})


df2 = df2[['url']].copy()
df2['type'] = 'phishing'

lf1 = lf1[['url']].copy()
lf1['type'] = 'benign'

#print(df1['type'].value_counts(normalize=True),"\t",len(df1))
#print(df2['type'].value_counts(normalize=True),"\t",len(df2))
#print(lf1['type'].value_counts(normalize=True),"\t",len(lf1))

combined_data = pd.concat([df1,df2,lf1])
combined_data = combined_data.drop_duplicates(subset=['url'])

print(combined_data)