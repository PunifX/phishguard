import pandas as pd
import requests as r
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse

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

def extraction_hyper_link(urls):
    #the data frame contains more than 1m links so executing this methode gonna take alot of time
    results = []
    for url in urls:
        try:
            response = r.get(url,timeout=5)
            soup =bs(response.text,"html.parser")
            link = soup.find_all("a")

            total = len(link)
            empty = sum(1 for i in link if not i.get("href") or i.get("href") in ["#", "" , "javascript:void(0);"])
            #return 1 for i in link if the object of href exist aka true and urlparse using netloc to get the domain != urlparse netloc of the url to get tthe domain
            external = sum(1 for i in link if i.get("href") and urlparse(i.get("href")).netloc != urlparse(url).netloc)
            internal = total - empty - external
            ratio = external / total if total > 0 else 0
            forms = soup.find_all("form")
            total_forms = len(forms)
            suspicious_forms = sum(1 for f in forms if f.get("action") and urlparse(f.get("action")).netloc != urlparse(url).netloc)

            results.append({
                "total_links":total,
                "empty_links":empty,
                "external_links":external,
                "internal_links":internal,
                "ratio_external_total":ratio,
                "total_forms":total_forms,
                "suspicious_forms":suspicious_forms
            })
            
        except:
            results.append({
                "total_links":0,
                "empty_links":0,
                "external_links":0,
                "internal_links":0,
                "ratio_external_total":0,
                "total_forms":0,
                "suspicious_forms":0

            })


    extraction_hyper_link =  pd.DataFrame(results)
    extraction_hyper_link.head()
    return extraction_hyper_link

def extraction_textual_content(urls):
    extraction_textual_content = pd.DataFrame()


    return extraction_textual_content
def extraction_dns(urls):
    extraction_dns = pd.DataFrame()


    return extraction_dns


url_patterns_features = extraction_url_patterns(urls)
hyper_link_features = extraction_hyper_link(urls)
textual_content_features = extraction_textual_content(urls)
dns_features  =  extraction_dns(urls)


#features = pd.concat([urls,url_patterns_features,hyper_link_features,textual_content_features,dns_features], axis=1)
features = pd.concat([url_patterns_features,hyper_link_features,textual_content_features,dns_features], axis=1)
#features.to_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\features.csv")
#prediction.to_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\prediction")




