import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import classification_report, confusion_matrix

import joblib

from xgboost import XGBClassifier

from sklearn.svm import SVC

from sklearn.linear_model import LogisticRegression


df = pd.read_csv('data/features_dataset.csv')


x = df.drop(columns=['url','type'])
y = df['type'] #predection so we get rid of everything else especiallyy the url

#print("features:",x.columns.tolist())
#print("shape:",x.shape)

#print(y.value_counts())


x_train , x_test , y_train , y_test = train_test_split (x,y,test_size=0.25,stratify=y,random_state=42)


print("training rows:",len(x_train))
print("testing rows:",len(x_test))

rndm_frst_model = RandomForestClassifier(n_estimators=100,random_state=42)
rndm_frst_model.fit(x_train,y_train)


y_pred = rndm_frst_model.predict(x_test)

print("radnomforest results:")
print(classification_report(y_test,y_pred))
print(confusion_matrix(y_test,y_pred))

joblib.dump(rndm_frst_model, 'src/models/phishguard_model.pkl')



# Convert labels to numbers (XGBoost needs 0 and 1, not text)
y_train_num = (y_train == 'phishing').astype(int)
y_test_num = (y_test == 'phishing').astype(int)

# Train XGBoost
xgb_model = XGBClassifier(n_estimators=100, random_state=42)
xgb_model.fit(x_train, y_train_num)


xgb_pred = xgb_model.predict(x_test)
print("XGBoost results:")
print(classification_report(y_test_num, xgb_pred))
print(confusion_matrix(y_test_num, xgb_pred))


joblib.dump(xgb_model, 'src/models/phishguard_xgb_model.pkl')

#it takes so long and it even crashed


#x_train_svm = x_train
#y_train_svm = y_train

#svm_model = SVC(kernel='rbf', random_state=42)
#svm_model.fit(x_train_svm, y_train_svm)
#svm_pred = svm_model.predict(x_test)

#print("SVM results")
#print(classification_report(y_test, svm_pred))


#linear regression

lr_model = LogisticRegression(random_state=42, max_iter=1000)
lr_model.fit(x_train, y_train)
lr_pred = lr_model.predict(x_test)
print("Logistic Regression results:")
print(classification_report(y_test, lr_pred))

joblib.dump(lr_model,'src/models/phishguard_linear_reg_model.pkl')