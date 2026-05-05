import pandas as pd
from sklearn.utils import resample

file1 = pd.read_csv(r"d:\codes\project\AI\improved version of phishguard\data\raw\legit_sites.csv")
file2 = pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\data\raw\phishing_site_urls.csv")
file3 = pd.read_csv(r"d:\codes\project\AI\improved version of phishguard\data\raw\malicious_phish2.csv")


file1['type'] = 'safe'
file1 ["url"] = "https://"+file1 ["url"]
file1 = file1[["url","type"]].copy()

file2.rename(columns={"Label":"type"}, inplace=True)
file2.rename(columns={"URL":"url"}, inplace=True)
file2["url"] = "https://" +file2["url"]
file2["type"] = "phishing"


file3 = file3[["url"]].copy()
file3["type"] = 'phishing'

total = pd.concat([file1,file2,file3])


total = total.dropna(subset="url").drop_duplicates(subset="url")
#print(total["type"].isnull().sum(),"\n--------\n",total["url"].duplicated().sum())


phishing = total[total["type"]=='phishing']
safe = total [total["type"] == 'safe']

safe_dwn = resample(safe,n_samples=len(phishing["url"]),random_state=42,replace=False)

final_data_frame = pd.concat([safe_dwn,phishing])
final_data_frame = final_data_frame.dropna().drop_duplicates(subset=("url"))
final_data_frame = final_data_frame.sample(frac=1,         
    replace=False,    
    random_state=42,  
    axis=0)


#print("\t\tF1\n",file1.shape,"\n",file1.head())
#print("\t\tF2\n",file2.shape,"\n",file2.head())
#print("\t\tF3\n",file3.shape,"\n",file3.head())

#print(phishing.head(),"\n",phishing.shape)
print(final_data_frame.head(),"\n",final_data_frame.shape,"\n","dups:",final_data_frame.duplicated().sum(),"\n","null:",final_data_frame.isnull().sum())

print(final_data_frame["type"].value_counts())
print(final_data_frame["type"].value_counts(normalize=True)) 

final_data_frame.to_csv(r"D:\codes\project\AI\improved version of phishguard\data\processed\final_data_frame.csv",index=False)