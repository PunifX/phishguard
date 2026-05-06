
import pandas as pd
saved = pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\dns_features.csv")
#print(saved.iloc[1120000])  # the original
#print(saved.iloc[-1])       # the extra one
saved = saved.drop(index=1120001).reset_index(drop=True)
saved.to_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\dns_features1.csv", index=False)

#print(saved.tail())
#print(saved.shape)

#print("---------")
#print(saved.iloc[1120000])  # where you resumed from
#print(saved.iloc[1120001])  # next one
#print("---------")
orginal = pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\data\processed\final_data_frame.csv")

#print(orginal.shape)
print(len(orginal))
print(len(saved))
#print(orginal.iloc[145])
#print("---------")
#print("---------")
#print("---------")
df = pd.read_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\test\hyper_textual_features.csv")
#df = df.drop(index=29996).reset_index(drop=True)
df = df.drop(index=30001).reset_index(drop=True)
df.to_csv(r"D:\codes\project\AI\improved version of phishguard\output\features\test\hyper_textual_features1.csv", index=False)

all_zeros = (df == 0).all(axis=1).sum()
print(f"All zero rows: {all_zeros}/{len(df)} = {all_zeros/len(df)*100:.1f}%")

