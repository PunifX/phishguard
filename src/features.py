import pandas as pd
import re

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
    extraction_hyper_link_features = pd.DataFrame()


    return extraction_hyper_link_features

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

print(features["fake_letters_counter"].sum())


