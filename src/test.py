import pandas as pd

final = pd.read_csv('data/features_dataset.csv')
final = final.sort_values('has_fake_letters')

fake_letters_set = set("а е о р с х і ј ѕ ѵ".split())

def check_fake_letters(url):
    return [c for c in url if c in fake_letters_set]
df = pd.read_csv('data/final_dataset.csv')
df['found_fake_letters'] = df['url'].apply(check_fake_letters)

print("Rows containing fake letters:")
print((df['found_fake_letters'].str.len() > 0).sum())

print(df[df['found_fake_letters'].str.len() > 0][['url', 'found_fake_letters']].head(10))