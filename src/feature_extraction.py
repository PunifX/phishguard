import pandas as pd
import re
from urllib.parse import urlparse



df = pd.read_csv('data/final_dataset.csv')

def extract_features(url):

    original_url = url
    url = re.sub(r'^https?://', '', url)  # remove http:// or https://
    url = re.sub(r'^www\.', '', url)       # remove www.
    url = url.strip('/')                   # remove trailing slash


    url_http = "http://" + url
    

    counter_dots = 0
    counter_numbers = 0
    counter_paths = 0
    symbols = 0
    counter_hyphens=0
    fake_letters_set = set("а е о р с х і ј ѕ ѵ".split())
    fake_letters = 0

   

    features = {}

    features ['url_length'] = len(url)

    for i in url:  
        if i == '.':
            counter_dots = counter_dots + 1
        if i.isdigit():
            counter_numbers= counter_numbers+ 1
        if i == '/':
            counter_paths=counter_paths + 1
        if i == '-':
            counter_hyphens =counter_hyphens +1
        if i in ["@","_","?","=","&","%"]:
            symbols = symbols +1
        if i in fake_letters_set:
                fake_letters += 1


    features ['num_dots']  = counter_dots

    features['num_digits'] = counter_numbers

    features['num_paths'] = counter_paths

    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

    features['is_an_ip'] = 1 if re.search(ip_pattern, url) else 0

    try:
        parsed = urlparse(url_http)
        hostname = parsed.netloc
    except ValueError:
        hostname = ""

    if hostname == "":
        features['num_subdomains'] = 0
    else:
        parts = hostname.split('.')
        features['num_subdomains'] = max(0, len(parts) - 2)

    features['num_hyphens'] = counter_hyphens
    features['has_suspicious_symbols'] = symbols
    #features['has_fake_letters'] = fake_letters

    return features

df = pd.read_csv('data/final_dataset.csv')    


feature_df = df['url'].apply(lambda url: pd.Series(extract_features(url)))

final = pd.concat([df,feature_df],axis = 1)
print(final.head())
print(final.shape)
final.to_csv('data/features_dataset.csv', index=False)
