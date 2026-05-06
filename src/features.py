import pandas as pd
import requests as r
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

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


def extraction_hyper_link_and_textual(urls):
    results = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i, result in enumerate(executor.map(fetch_one, urls)):
            results.append(result)
            if i % 10000 == 0:
                pd.DataFrame(results).to_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\hyper_textual_features.csv", index=False)
                print(f"Progress: {i}/{len(urls)}")
    
    extraction_hyper_link_and_textual= pd.DataFrame(results)
    return extraction_hyper_link_and_textual

 
def extraction_dns(urls):
    
    extraction_dns = pd.DataFrame()


    return extraction_dns


url_patterns_features = extraction_url_patterns(urls)
e_h_l_a_t = extraction_hyper_link_and_textual(urls)
#e_h_l_a_t = pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\hyper_textual_features.csv")
dns_features  =  extraction_dns(urls)


#features = pd.concat([urls,url_patterns_features,hyper_link_features,textual_content_features,dns_features], axis=1)
features = pd.concat([url_patterns_features,e_h_l_a_t,dns_features], axis=1)
#features.to_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\features.csv")
#prediction.to_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\prediction")




