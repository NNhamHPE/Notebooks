import joblib
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from xgboost.sklearn import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
model = joblib.load("tuned decision tree.pkl")
xaxis = pd.read_csv("xaxis.csv")
yaxis = pd.read_csv("yaxis.csv")
xtest = pd.read_csv("xtest.csv")
ytest = pd.read_csv("ytest.csv")

option = 3
if option == 0:
    model = DecisionTreeClassifier(random_state = 8)
    model.fit(xaxis, yaxis)
if option == 1:
    model = model
if option == 2:
    model = XGBClassifier()
    model.fit(xaxis, yaxis)
if option == 3:
    model = RandomForestClassifier(random_state=8)
    model.fit(xaxis, yaxis.values.ravel())

reqidcol = pd.DataFrame(xtest["ReqMasterId"])

prediction = model.predict(xtest)
predictionpd = pd.DataFrame(prediction, columns=["ProjectedDays"])
predictionpd = pd.concat([reqidcol, predictionpd], axis=1)
predictionpd.to_csv("tuned results.csv", index=False)

print("Finish")

#import matplotlib.pyplot as plt
#import sklearn.tree as tree
#fig = plt.figure(figsize=(20,20))
#thing = tree.plot_tree(model, feature_names=None, class_names=None, filled=True)
#plt.show()

#import sklearn.tree as tree
#texttree = tree.export_text(model)
#print(texttree)

#print(predictionpd["ProjectedDays"].value_counts())
