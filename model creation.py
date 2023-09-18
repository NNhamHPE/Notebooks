import time
start = time.time()
import datetime
curTime = datetime.datetime.now().strftime("%H:%M:%S")
print("Start Time: ", curTime)
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
import joblib

runTimeBool = True

gridParams = {
    "random_state": [8],
    "max_depth": [20, 50, 100, None],
    "criterion": ["gini", "entropy", "log_loss"],
    "min_samples_leaf": [1, 10, 100, 1000],
    "min_weight_fraction_leaf": [0.0, 0.05, 0.1, 0.2],
    "max_features": ["log2", "sqrt", None],
    "max_leaf_nodes": [None, 20, 50, 100]
              }

totModels = 1
for index, (key, value) in enumerate(gridParams.items()):
    if index == 0:
        totMpdels = len(value)
    else:
        totModels = totModels*len(value)
print(f"Total models to explore: {totModels}")

xaxis = pd.read_csv("xaxis.csv")
yaxis = pd.read_csv("yaxis.csv")

gridTest = GridSearchCV(estimator=RandomForestClassifier(), param_grid = gridParams, cv = 2, #n_jobs =-1
)
gridTest.fit(xaxis, yaxis.values.ravel())
joblib.dump(gridTest.best_estimator_, "tuned decision tree.pkl")
if runTimeBool == True:
    checkpoint = round(time.time()-start, 2)
    print(f"Export PKL File: {checkpoint}\n")
printGridTest = True
if printGridTest == True:
    print(f"\n ======================")
    print("\n Best params: ", gridTest.best_params_)
    print("\n Best score: ", gridTest.best_score_)
    print("\n========================\n")

if runTimeBool == True:
    checkpoint = round(time.time()-start, 2)
    print(f"Finish Runtime: {round(checkpoint/60, 0)} minutes, {round(checkpoint%60, 2)} seconds")
