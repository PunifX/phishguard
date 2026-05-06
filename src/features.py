import pandas as pd
import requests as r
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import dns.resolver
import dns.exception
from bs4 import XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

data_frame = pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\data\processed\final_data_frame.csv")
urls = data_frame["url"]
prediction = data_frame["type"]
features  = pd.DataFrame()


def extraction_url_patterns(urls):
    cleaned_url = urls.str.replace("https://","")
    extraction_url_patterns_features = pd.DataFrame()
   

    extraction_url_patterns_features["url_length"] = cleaned_url.str.len()
    extraction_url_patterns_features["dots_counter"] = cleaned_url.str.count(r"\.")
    extraction_url_patterns_features["numbers_counter"] = cleaned_url.str.count(r"\d")
    extraction_url_patterns_features["hyphens_counter"] = cleaned_url.str.count("-")
    extraction_url_patterns_features["symbol_counter"] = cleaned_url.str.count(r"[@_?=&%]")
    extraction_url_patterns_features["fake_letters_counter"] =cleaned_url.str.count(r"[аеорсхіјѕѵ]")
    extraction_url_patterns_features["has_ip"] = cleaned_url.str.contains(r"\d+\.\d+\.\d+\.\d+").astype(int)
    
    
    return extraction_url_patterns_features




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

def extraction_hyper_link_and_textual(urls, start_from=0):
    results = []
    urls_list = list(urls)[start_from:]

    with ThreadPoolExecutor(max_workers=200) as executor:
        for i, result in enumerate(executor.map(fetch_one, urls_list)):
            results.append(result)
            if i % 10000 == 0:
                pd.DataFrame(results).to_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\hyper_textual_features.csv", index=False)
                print(f"Progress: {start_from + i}/{len(urls)}")
    
    extraction_hyper_link_and_textual= pd.DataFrame(results)
    return extraction_hyper_link_and_textual

def fetch_one_dns(url):
    try:
        domain = urlparse(url).netloc
        try:
            
            a_records = dns.resolver.resolve(domain,"A")
            has_a = 1
            ttl = a_records.rrset.ttl
        except:
            has_a = 0
            ttl = 0
        
        try:
            dns.resolver.resolve(domain,"MX")
            has_mx = 1
        except:
            has_mx = 0

        try:
            txt_records = dns.resolver.resolve(domain, "TXT")
            has_spf = 1 if any("spf" in str(record).lower() for record in txt_records) else 0
        except:
            has_spf = 0

        return {"has_a": has_a, "ttl": ttl, "has_mx": has_mx, "has_spf": has_spf}
    
    except:
        return {"has_a":0,"ttl":0,"has_mx":0,"has_spf":0 }    

def extraction_dns(urls,start_from=0):
    results = []
    urls_list = list(urls)[start_from:]
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i, result in enumerate(executor.map(fetch_one_dns, urls_list)):
            results.append(result)
            if i % 10000 == 0:
                pd.DataFrame(results).to_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\dns_features.csv", index=False)
                print(f"Progress: {start_from + i}/{len(urls)}")
    
    extraction_dns = pd.DataFrame(results)
    return extraction_dns


url_patterns_features = extraction_url_patterns(urls)


#e_h_l_a_t = extraction_hyper_link_and_textual(urls)
#e_h_l_a_t = extraction_hyper_link_and_textual(urls, start_from=x)
#e_h_l_a_t = pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\hyper_textual_features.csv")

#dns_features  =  extraction_dns(urls)
#dns_features = extraction_dns(urls, start_from=x)
dns_features =pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\dns_final.csv")


features = pd.concat([urls,url_patterns_features,dns_features], axis=1)
#features = pd.concat([url_patterns_features,e_h_l_a_t,dns_features], axis=1)
features.to_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\features_final.csv")
#prediction.to_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\prediction")




