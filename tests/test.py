import joblib
import pandas as pd

model = joblib.load('src/models/phishguard_model.pkl')

features = ['url_length', 'num_dots', 'num_digits', 'num_paths', 
            'is_an_ip', 'num_subdomains', 'num_hyphens', 'has_suspicious_symbols']

importances = model.feature_importances_

for f, i in sorted(zip(features, importances), key=lambda x: x[1], reverse=True):
    print(f"{f}: {i:.4f}")

df = pd.read_csv('data/features_dataset.csv')

print("=== PHISHING URLs averages ===")
print(df[df['type']=='phishing'][['url_length','num_paths','num_dots','num_digits','num_hyphens','num_subdomains']].mean().round(2))

print("\n=== BENIGN URLs averages ===")
print(df[df['type']=='benign'][['url_length','num_paths','num_dots','num_digits','num_hyphens','num_subdomains']].mean().round(2))