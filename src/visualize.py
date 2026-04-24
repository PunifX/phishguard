import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from xgboost import XGBClassifier
import joblib


df = pd.read_csv('data/features_dataset.csv')
x = df.drop(columns=['url', 'type'])
y = df['type']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, stratify=y, random_state=42)
y_test_num = (y_test == 'phishing').astype(int)

#Load models
rf_model  = joblib.load('src/models/phishguard_model.pkl')
xgb_model = joblib.load('src/models/phishguard_xgb_model.pkl')
lr_model  = joblib.load('src/models/phishguard_linear_reg_model.pkl')

#Get predictions
rf_pred  = rf_model.predict(x_test)
xgb_pred = xgb_model.predict(x_test)
lr_pred  = lr_model.predict(x_test)

# Convert xgb predictions back to text for consistency
xgb_pred_text = ['phishing' if p == 1 else 'benign' for p in xgb_pred]

#CHART 1: Model Comparison Bar Chart
models     = ['Random Forest', 'XGBoost', 'Logistic Regression']
accuracies = [0.87, 0.86, 0.75]
precisions = [0.87, 0.86, 0.79]
recalls    = [0.87, 0.87, 0.68]
f1_scores  = [0.87, 0.86, 0.73]

x_pos = np.arange(len(models))
width = 0.2

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(x_pos - width*1.5, accuracies, width, label='Accuracy',  color='steelblue')
ax.bar(x_pos - width*0.5, precisions, width, label='Precision', color='seagreen')
ax.bar(x_pos + width*0.5, recalls,    width, label='Recall',    color='tomato')
ax.bar(x_pos + width*1.5, f1_scores,  width, label='F1 Score',  color='gold')

ax.set_xticks(x_pos)
ax.set_xticklabels(models)
ax.set_ylim(0, 1.1)
ax.set_ylabel('Score')
ax.set_title('Model Comparison')
ax.legend()
plt.tight_layout()
plt.savefig('src/models/model_comparison.png')
plt.show()
print("Chart 1 saved!")

#CHART 2: Confusion Matrices
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

cms = [
    confusion_matrix(y_test, rf_pred),
    confusion_matrix(y_test, xgb_pred_text),
    confusion_matrix(y_test, lr_pred)
]
titles = ['Random Forest', 'XGBoost', 'Logistic Regression']

for ax, cm, title in zip(axes, cms, titles):
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['benign', 'phishing'],
                yticklabels=['benign', 'phishing'])
    ax.set_title(title)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')

plt.tight_layout()
plt.savefig('src/models/confusion_matrices.png')
plt.show()
print("Chart 2 saved!")

#CHART 3: Feature Importance (Random Forest only)
feature_names = x.columns.tolist()
importances   = rf_model.feature_importances_

fi_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
fi_df = fi_df.sort_values('importance', ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(fi_df['feature'], fi_df['importance'], color='steelblue')
ax.set_title('Feature Importance - Random Forest')
ax.set_xlabel('Importance')
plt.tight_layout()
plt.savefig('src/models/feature_importance.png')
plt.show()
print("Chart 3 saved!")

print("\nAll charts saved to src/models/")