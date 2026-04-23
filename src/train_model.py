import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import classification_report, confusion_matrix

import joblib

df = pd.read_csv('data/features_dataset.csv')


x = df.drop(columns=['url','type'])
y = df['type'] #predection so we get rid of everything else especiallyy the url

#print("features:",x.columns.tolist())
#print("shape:",x.shape)

print(y.value_counts())


x_train , x_test , y_train , y_test = train_test_split (x,y,
                                                       test_size=0.25,
                                                       random_state=42)


print("training rows:",len(x_train))
print("testing rows:",len(x_test))

model = RandomForestClassifier(n_estimators=100,random_state=42)
model.fit(x_train,y_train)

y_pred = model.predict(x_test)

print(classification_report(y_test,y_pred))
print(confusion_matrix(y_test,y_pred))

joblib.dump(model, 'src/models/phishguard_model.pk1')
