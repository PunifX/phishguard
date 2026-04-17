import pandas as pd
import re
from urllib.parse import urlparse
import joblib



model = joblib.load('src/models/phishguard_model.pk1')



def extract_features(url):
    counter_dots = 0
    counter_numbers = 0
    counter_paths = 0
    symbols = 0
    counter_hyphens=0
    fake_letters_set = set("а е о р с х і ј ѕ ѵ".split())
    fake_letters = 0

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
    features['has_symbols'] = symbols
    #features['has_fake_letters'] = fake_letters

    return features


while True:
    url = input("enter URL : ")
    if url == 'quit':
        break
    features = extract_features(url)
    x = pd.DataFrame([features])
    prediction = model.predict(x)[0]
    probability = model.predict_proba(x)[0]
        
    print(f"Prediction: {prediction.upper()}")
    print(f"Confidence: {max(probability)*100:.1f}%")


    
