import pandas as pd
import re
counter_dots = 0
counter_numbers = 0
df = pd.read_csv('data/final_dataset.csv')

def extract_features(url):
    features = {}

    features ['url_length'] = len(url)


    for i in url:  
        if i == '.':
            counter_dots+=1
        if i.isdigit():
            counter_numbers+=1

    features ['num_dots']  = counter_dots

    features['num_digitals'] = counter_numbers

    features['has_https']

    features['has_ip']

    features['num_subdomains']

    features['num_paths']

    return features