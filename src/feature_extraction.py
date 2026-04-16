import pandas as pd
import re
from urllib.parse import urlparse



df = pd.read_csv('data/final_dataset.csv')

def extract_features(url):
    counter_dots = 0
    counter_numbers = 0
    counter_paths = 0
    symbols = 0
    fake_letters = 0
    counter_hyphens=0

    if not url.startswith("http://") and not url.startswith("https://"):
        url_http = "http://" + url
    else:
        url_http = url 
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
        if i in ["@","_","?","=","&","%",":"]:
            symbols = symbols +1
        if i in ["а","е","о","р","с","х"]:
            fake_letters = fake_letters + 1

    features ['num_dots']  = counter_dots

    features['num_digits'] = counter_numbers

    features['num_paths'] = counter_paths

    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

    features['is_an_ip'] = 1 if re.search(ip_pattern, url) else 0

    parsed = urlparse(url_http)
    #print(parsed)
    
    hostname = parsed.netloc

    if hostname == "":
        features['num_subdomains'] = 0
        return features
    else:
        parts = hostname.split('.')
        final = max(0,len(parts) - 2)

    features['num_subdomains'] = final

    features ['num_hyphens'] = counter_hyphens
    
    features ['has_at_symbol'] = symbols
    features ['has_fake_letters'] = fake_letters
    
    return features
    
url = str(input())
features = extract_features(url)
print(features)