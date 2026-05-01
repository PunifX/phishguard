from flask import Flask, request, jsonify, render_template, url_for
import pandas as pd
import re
from urllib.parse import urlparse
import joblib
import os
import requests
from pathlib import Path


basedir = os.path.dirname(os.path.abspath(__file__))

# Create Flask app with proper static and template folders
app = Flask(__name__, 
            template_folder=os.path.join(basedir, 'templates'),
            static_folder=os.path.join(basedir, 'static'))

# Model loading from HuggingFace 

HF_BASE = "https://huggingface.co/PunifX/phishguard-models/resolve/main"

MODEL_FILES = {
    "rf":  "phishguard_model.pkl",
    "xgb": "phishguard_xgb_model.pkl",
    "lr":  "phishguard_linear_reg_model.pkl",
}

CACHE_DIR = Path(basedir) / "models_cache"
CACHE_DIR.mkdir(exist_ok=True)

def load_model(filename):
    local_path = CACHE_DIR / filename
    if not local_path.exists():
        print(f"Downloading {filename} from HuggingFace")
        r = requests.get(f"{HF_BASE}/{filename}", stream=True)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f" {filename} cached.")
    else:
        print(f" {filename} loaded from cache.")
    return joblib.load(local_path)

print("Loading models...")
model_rf  = load_model(MODEL_FILES["rf"])
model_xgb = load_model(MODEL_FILES["xgb"])
model_lr  = load_model(MODEL_FILES["lr"])
print("All models ready.")


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

    return features


def get_suspicious_reasons(features):
    reasons = []

    
    if features['url_length'] > 40:
        reasons.append(f"URL is long ({features['url_length']} chars) — phishing URLs average 55 chars vs 27 for safe ones")

    if features['num_paths'] > 1:
        reasons.append(f"Deep path structure ({features['num_paths']} levels) — phishing URLs use deep paths to look legitimate")

    if features['num_dots'] > 2:
        reasons.append(f"Many dots ({features['num_dots']}) — possible subdomain abuse like evil.fake.bank.com")

    if features['num_digits'] > 4:
        reasons.append(f"Many digits ({features['num_digits']}) — random-looking URLs often indicate phishing")

    if features['num_hyphens'] > 1:
        reasons.append(f"Multiple hyphens ({features['num_hyphens']}) — used in tricks like paypal-secure-login.ru")

    if features['num_subdomains'] > 1:
        reasons.append(f"Multiple subdomains ({features['num_subdomains']}) — legitimate sites rarely need many subdomains")

    if features['is_an_ip'] == 1:
        reasons.append("Uses an IP address instead of a domain — legitimate sites never do this")

    if features['has_suspicious_symbols'] > 0:
        reasons.append("Contains suspicious symbols (@, ?, =, %) — possible URL manipulation")

    return reasons if reasons else ["No suspicious patterns detected — URL looks clean"]

@app.route('/')
def home():
    
    return render_template('index.html')

@app.route('/predict', methods=['POST'])

def predict():
    
    data = request.get_json()
    url  = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    features = extract_features(url)
    x        = pd.DataFrame([features])

    # Random Forest
    rf_pred  = str(model_rf.predict(x)[0])
    rf_proba = model_rf.predict_proba(x)[0]
    rf_conf  = round(float(max(rf_proba)) * 100, 1)

    # XGBoost
    xgb_pred_num = model_xgb.predict(x)[0]
    xgb_pred     = 'phishing' if xgb_pred_num == 1 else 'benign'
    xgb_proba    = model_xgb.predict_proba(x)[0]
    xgb_conf     = round(float(max(xgb_proba)) * 100, 1)

    # Logistic Regression
    lr_pred  = str(model_lr.predict(x)[0])
    lr_proba = model_lr.predict_proba(x)[0]
    lr_conf  = round(float(max(lr_proba)) * 100, 1)

    reasons = get_suspicious_reasons(features)

    return jsonify({
        'url': url,
        'models': {
            'random_forest': {
                'prediction': rf_pred,
                'confidence': rf_conf,
                'recommended': True
            },
            'xgboost': {
                'prediction': xgb_pred,
                'confidence': xgb_conf,
                'recommended': False
            },
            'logistic_regression': {
                'prediction': lr_pred,
                'confidence': lr_conf,
                'recommended': False
            }
        },
        'reasons': reasons,
        'features': {k: int(v) if isinstance(v, (int,)) else float(v) for k, v in features.items()}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0')