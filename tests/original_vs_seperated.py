import pandas as pd
import random
from urllib.parse import urlparse
import dns.resolver
import requests as r
from bs4 import BeautifulSoup as bs
from bs4 import XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

original = pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\data\processed\final_data_frame.csv")
dns_saved = pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\dns_features1.csv")
hyper_textual_saved_original = pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\test\hyper_textual_features1.csv")
hyper_textual_saved = pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\test\hyper_textual_features1.csv")

def fetch_one(url):
    try:
        response = r.get(url, timeout=5)
        soup = bs(response.text, "html.parser")

        # hyperlink features
        link = soup.find_all("a")
        total = len(link)

        empty = sum(1 for i in link if not i.get("href") or i.get("href") in ["#", "", "javascript:void(0);"])
        external = sum(1 for i in link if i.get("href") and urlparse(i.get("href")).netloc and urlparse(i.get("href")).netloc != urlparse(url).netloc)
        internal = total - empty - external
        ratio = external / total if total > 0 else 0

        forms = soup.find_all("form")
        total_forms = len(forms)
        suspicious_forms = sum(1 for f in forms if f.get("action") and urlparse(f.get("action")).netloc and urlparse(f.get("action")).netloc != urlparse(url).netloc)

        # textual features
        title = soup.title.string.lower() if soup.title and soup.title.string else ""
        domain = urlparse(url).netloc

        title_match = 1 if domain in title else 0

        text = soup.get_text().lower()
        has_copyright = 1 if "©" in text or "copyright" in text else 0
        iframes = len(soup.find_all("iframe"))
        password_fields = len(soup.find_all("input", {"type": "password"}))
        has_favicon = 1 if soup.find("link", rel="icon") or soup.find("link", rel="shortcut icon") else 0
        has_meta = 1 if soup.find("meta", {"name": "description"}) else 0

        return {
            # hyperlink
            "total_links": total, "empty_links": empty, "external_links": external,
            "internal_links": internal, "ratio_external_total": ratio,
            "total_forms": total_forms, "suspicious_forms": suspicious_forms,
            # textual
            "title_match": title_match, "has_copyright": has_copyright,
            "iframes": iframes, "password_fields": password_fields,
            "has_favicon": has_favicon, "has_meta": has_meta
        }

    except:
        return {
            "total_links": 0, "empty_links": 0, "external_links": 0,
            "internal_links": 0, "ratio_external_total": 0,
            "total_forms": 0, "suspicious_forms": 0,
            "title_match": 0, "has_copyright": 0,
            "iframes": 0, "password_fields": 0,
            "has_favicon": 0, "has_meta": 0
        }

indexes = random.sample(range(1120000, 1128666), 5)

for idx in indexes:
    url = original["url"].iloc[idx]
    domain = urlparse(url).netloc
    print(f"\nIndex: {idx} | URL: {url}")

    # # DNS comparison
    try:
        a_records = dns.resolver.resolve(domain, "A")
        has_a = 1
        ttl = a_records.rrset.ttl
    except:
        has_a = 0
        ttl = 0

    try:
        dns.resolver.resolve(domain, "MX")
        has_mx = 1
    except:
        has_mx = 0

    try:
        txt_records = dns.resolver.resolve(domain, "TXT")
        has_spf = 1 if any("spf" in str(rec).lower() for rec in txt_records) else 0
    except:
        has_spf = 0

    dns_live = {"has_a": has_a, "ttl": ttl, "has_mx": has_mx, "has_spf": has_spf}
    dns_saved_row = dns_saved.iloc[idx].to_dict()
    print(f"DNS Live:  {dns_live}")
    print(f"DNS Saved: {dns_saved_row}")
    print(f"DNS Match - has_a: {dns_live['has_a'] == dns_saved_row['has_a']} | has_mx: {dns_live['has_mx'] == dns_saved_row['has_mx']} | has_spf: {dns_live['has_spf'] == dns_saved_row['has_spf']}")

    # Hypertextual comparison
    # hyper_live = fetch_one(url)
    # hyper_saved_row = hyper_textual_saved.iloc[idx].to_dict()
    # print(f"\nHypertextual Live:  {hyper_live}")
    # print(f"Hypertextual Saved: {hyper_saved_row}")
    # for key in hyper_live:
    #     match = hyper_live[key] == hyper_saved_row[key]
    #     print(f"  {key}: {match}")