Python modules that are needed:<br>
Time, Datetime, IO, SQLAlchemy, NumPy, SciPy, Pandas, Scikit-learn, joblib (optional)
<br><br>
Additional Notes Moving Forward:<br>
The current model runs the default parameters for Scikit-learn's RandomForestClassifier which is an ensemble model that creates multiple decision trees per prediction and has them "vote" on the outcome depending on the decisions made for that tree. However, as the dataset grows, it may be more appropriate in the future to switch to a regression model and change the target from the 15-day buckets to the actual number of days. It also may help to start using hyperparameter tuning in order to improve the accuracy of the model and prevent overtuning. "model creation.py" is a Python script that runs a Grid Search Cross Validation test for RandomForestClassifier which attempts to find the best model based on the parameters you give it to test. The script will export the model using joblib and it can be loaded and used in the prediction script.
<br><br>
Feel free to contact me if you have any questions: <br>
Phone: (916)-316-6268 <br>
School Email: nsnham@ucsc.edu <br>
Personal Email: 8nham8@gmail.com
