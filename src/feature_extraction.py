import pandas as pd
import re
from urllib.parse import urlparse
import requests


df = pd.read_csv('data/final_dataset.csv')

def extract_features(url):

    counter_dots = 0
    counter_numbers = 0
    counter_paths = 0
    starts_with_https = False

    features = {}

    features ['url_length'] = len(url)


    for i in url:  
        if i == '.':
            counter_dots = counter_dots + 1
        if i.isdigit():
            counter_numbers= counter_numbers+ 1
        if i == '/':
            counter_paths=counter_paths + 1
            

    features ['num_dots']  = counter_dots

    features['num_digits'] = counter_numbers

    features['num_paths'] = counter_paths

    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

    features['is_an_ip'] = 1 if re.search(ip_pattern, url) else 0

    parsed = urlparse(url)
    #print(parsed)
    
    hostname = parsed.netloc

    if hostname == "":
        features['num_subdomains'] = 0
        return features
    else:
        parts = hostname.split('.')
        final = max(0,len(parts) - 2)

    features['num_subdomains'] = final

    
    return features
    
url = str(input())
features = extract_features(url)
print(features)