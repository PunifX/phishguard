import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import classification_report, confusion_matrix

import joblib

from xgboost import XGBClassifier

from sklearn.svm import SVC

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score

x = pd.read_csv(r"D:\codes\project\AI\phishguard\output\features\features_final.csv")

y = pd.read_csv(r"D:\codes\project\AI\phishguard\data\processed\final_data_frame.csv")
y = y["type"] 
all_results = []  


x_train,x_test,y_train,y_test = train_test_split(x,y
                                                 ,test_size=0.25,stratify=y,random_state=42)
for n in [100,150,200,250,300,350]:
    print("\n\n!!-----------------",n,"-----------------!!")
    rndm_model = RandomForestClassifier(n_estimators=n,random_state=42,n_jobs=-1)
    rndm_model.fit(x_train,y_train)
    y_rndm_pred = rndm_model.predict(x_test)

    print("\n--------------\nradnomforest results:")
    print(classification_report(y_test,y_rndm_pred))
    print("\nconfusion matrix:")
    print(confusion_matrix(y_test,y_rndm_pred))

    acc = accuracy_score(y_test, y_rndm_pred)
    recall = recall_score(y_test, y_rndm_pred, pos_label="phishing")
    all_results.append(("RandomForest", f"n_estimators={n}", acc,recall))
    print(f"RandomForest  n={n}  accuracy={acc:.4f}")

    print("\n\n")


y_train_xgb = (y_train == "phishing").astype(int)
y_test_xgb = (y_test == "phishing").astype(int)
for n in [100,150,200,250,300,350]:
    print("\n\n!!-----------------",n,"-----------------!!")
    XGboost_model = XGBClassifier(n_estimators=n, random_state=42,n_jobs=-1)
    XGboost_model.fit(x_train,y_train_xgb)
    y_xgb_pred = XGboost_model.predict(x_test)

    print("\n--------------\nradnomforest results:")
    print(classification_report(y_test_xgb,y_xgb_pred))
    print("\nconfusion matrix:")
    print(confusion_matrix(y_test_xgb,y_xgb_pred))

    acc = accuracy_score(y_test_xgb, y_xgb_pred)
    recall = recall_score(y_test_xgb, y_xgb_pred, pos_label=1)
    all_results.append(("XGBoost", f"n_estimators={n}", acc,recall))
    print(f"XGBoost       n={n}  accuracy={acc:.4f}")
      
    print("\n\n")




for n in [500,1000,1500,2000,2500]:
    lr_model = LogisticRegression(max_iter=n, random_state=42, n_jobs=-1)
    lr_model.fit(x_train,y_train)
    y_lr_pred = lr_model.predict(x_test)

    print("\n--------------\nradnomforest results:")
    print(classification_report(y_test,y_lr_pred))
    print("\nconfusion matrix:")
    print(confusion_matrix(y_test,y_lr_pred))
    acc = accuracy_score(y_test, y_lr_pred)
    recall = recall_score(y_test, y_lr_pred, pos_label="phishing")
    all_results.append(("Logistic_regression", f"n={n}", acc, recall))
    print(f"LogisticReg   accuracy={acc:.4f}")



all_results.sort(key=lambda x: x[3], reverse=True)

for model, setting, acc, recall in all_results:
    print(f"{model:<20} {setting:<20} acc={acc:.4f}  recall={recall:.4f}")

best_model, best_setting, best_acc, best_recall = all_results[0]
print(f"\nBEST: {best_model}  {best_setting}  acc={best_acc:.4f}  recall={best_recall:.4f}")