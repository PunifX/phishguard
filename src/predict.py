import pandas as pd
import re
from urllib.parse import urlparse
import joblib

#rndm forest model
model_rndm_forest = joblib.load('src/models/phishguard_model.pkl')

#xgb forest
model_xgb = joblib.load('src/models/phishguard_xgb_model.pkl')

#linear regression
model_lr = joblib.load('src/models/phishguard_linear_reg_model.pkl')

def extract_features(url):
    original = url
    
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
    # Capture protocol BEFORE stripping
     
    #if original.startswith('https://'):
        #features['is_https'] = 1
    #else:
        #features['is_https'] = 0

    
    #if re.match(r'^https?://', original):
        #features['has_protocol'] = 1 
    #else:
        #features['has_protocol'] = 0

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
            symbols += 1
        if i in fake_letters_set:
                fake_letters += 1


    features ['num_dots']  = counter_dots

    features['num_digits'] = counter_numbers

    features['num_paths'] = counter_paths

    ip_pattern = r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b'

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


while True:
    url = input("enter URL : ")
    if url == 'quit':
        break
    features = extract_features(url)
    x = pd.DataFrame([features])
    #prediction random forest
    prediction_rndmforest = model_rndm_forest.predict(x)[0]
    probability_rndmforest= model_rndm_forest.predict_proba(x)[0]

    print("random forest predection:")    
    print(f"Prediction: {prediction_rndmforest.upper()}")
    print(f"Confidence: {max(probability_rndmforest)*100:.1f}%")

    print("\n------------------------------------")

    
    #prediction xgb

    prediction_xgb = model_xgb.predict(x)[0]

    label_xgb = "PHISHING" if prediction_xgb == 1 else "BENIGN"
    
    probability_xgb= model_xgb.predict_proba(x)[0]


    print("xgb predection:")    
    print(f"Prediction: {label_xgb}")
    print(f"Confidence: {max(probability_xgb)*100:.1f}%")

    print("\n------------------------------------")

    #prediction linear regression

    prediction_lr = model_lr.predict(x)[0]
    probability_lr = model_lr.predict_proba(x)[0]
    print("Logistic Regression prediction:")
    print(f"Prediction: {prediction_lr.upper()}")
    print(f"Confidence: {max(probability_lr)*100:.1f}%")

    
    print("\n------------------------------------")