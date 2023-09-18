import time
start = time.time()
import datetime
now = datetime.datetime.now()
curTime = now.strftime("%H:%M:%S")
print("Start Time: ", curTime)
import pandas as pd
import numpy as np
import sqlalchemy as sqla
import io
from sklearn.preprocessing import OneHotEncoder
import math

runTimeBool = True

if runTimeBool == True:
    checkpoint = round(time.time()-start, 2)
    print(f"Module import runtime: {checkpoint}")

getDataFromSQL = True
if getDataFromSQL == True:
    
    server = "hpeanneops.rose.rdlabs.hpecorp.net"
    username = "ops_aruba_writer"
    password = "W0nderfu1Pa55w0rd"
    db = "NEO"
    driver = "ODBC Driver 17 for SQL Server"

    dbconnection = f"mssql://{username}:{password}@{server}/{db}?driver={driver}"
    engine = sqla.create_engine(dbconnection)
    connection = engine.connect()

    sqltopandasdf = pd.read_sql("SELECT	R.ReqMasterId, R.EMPType, R.ReqStatus, R.NbofReqs, R.HiringManagerName, R.HiringManagerId, \
    R.REQApprovalDate, R.CostCenter, R.City, R.Country, R.JobFamily, R.JobCode, \
    (SELECT TOP  1 P.[month] + '-01' FROM HeadcountPlan P WHERE P.ReqNumber = R.ReqNumber ORDER BY P.[month] desc) AS StartDate \
    FROM	RequisitionMaster R \
    WHERE	(SELECT TOP  1 P.[month] + '-01' FROM HeadcountPlan P WHERE P.ReqNumber = R.ReqNumber ORDER BY P.[month] desc) IS NOT NULL \
    and R.ReqStatus <> 'Closed' and R.EMPType <> 'INT'", engine)
    
    sqltopandasdf.to_csv("compiledata.csv", index=False)
    
    if runTimeBool == True:
        checkpoint = round(time.time()-start, 2)
        print(f"Database import runtime: {checkpoint}")
    
initialcsv = "compiledata.csv"
try:
    with io.open("compiledata.csv", encoding="ANSI") as outer:
        with io.open("convertedcompileddata.csv", "w", encoding="UTF-8") as inner:
            for line in outer:
                inner.write(line)
except:
    dummydf = pd.read_csv("convertedcompileddata.csv", index_col=False)
    dummydf.to_csv("convertedcompileddata.csv", index=False)

pandasdf = pd.read_csv("convertedcompileddata.csv", index_col=False)
if runTimeBool == True:
    checkpoint = round(time.time()-start, 2)
    print(f"UTF-8 Conversion runtime: {checkpoint}")

def findDupeCols(pandasdf):
    dupeCols = set()
    for x in range(pandasdf.shape[1]):
        col = pandasdf.iloc[:,x]
        for y in range(x+1,pandasdf.shape[1]):
            col2 = pandasdf.iloc[:,y]
            if col.equals(col2):
                dupeCols.add(pandasdf.columns.values[x])
    return list(dupeCols)
dupecols = findDupeCols(pandasdf)
pandasdf.drop(columns = dupecols, inplace=True)

for index, row in pandasdf.iterrows():
    if row["ReqStatus"].lower() == "closed":
        pandasdf.drop(index, axis=0, inplace=True)
pandasdf = pandasdf.reset_index(drop=True)

clearCompleteDupeReqs = True
alsoClearUncompleteDupes = False
if clearCompleteDupeReqs == True:
    dupeRecList = []
    ucDupeRecList = []
    for index, row in pandasdf.iterrows():
        if row["NbofReqs"] > 1:
            concatRow = str(row["NbofReqs"]) + str(row["City"]) + str(row["HiringManagerName"] + str(row["REQApprovalDate"]))
            if row["ReqStatus"] == "Filled" or row["ReqStatus"] == "Filled in WD with open status":
                if concatRow in dupeRecList:
                    pandasdf.drop(index, inplace=True)
                else:
                    dupeRecList.append(concatRow)
            else:
                if alsoClearUncompleteDupes == True:
                    if concatRow in ucDupeRecList:
                        pandasdf.drop(index, inplace=True)
                    else:
                        ucDupeRecList.append(concatRow)
                else:
                    pass
pandasdf.reset_index()

if getDataFromSQL == True:
    pandasdf["REQApprovalDate"] = pd.to_datetime(pandasdf["REQApprovalDate"], format="%Y-%m-%d")
    pandasdf["StartDate"] = pd.to_datetime(pandasdf["StartDate"], format="%Y-%m-%d")
else:
    pandasdf["REQApprovalDate"] = pd.to_datetime(pandasdf["REQApprovalDate"], format="%m/%d/%Y")
    pandasdf["StartDate"] = pd.to_datetime(pandasdf["StartDate"], format="%m/%d/%Y")

ununiqueCols = [x for x in pandasdf.columns if pandasdf[x].nunique()==1]
pandasdf.drop(ununiqueCols, axis=1, inplace=True)

edgedate = "1905-01-01 00:00:00"
edgedate64 = np.datetime64(edgedate)
for date in pandasdf["StartDate"]:
    if date < edgedate64:
        pandasdf.drop(pandasdf.index[(pandasdf["StartDate"] == date)], axis=0, inplace=True)
for date in pandasdf["REQApprovalDate"]:
    if date < edgedate64:
        pandasdf.drop(pandasdf.index[(pandasdf["REQApprovalDate"] == date)], axis=0, inplace=True)
pandasdf = pandasdf.reset_index(drop=True)

yTestStartDates = []
for index, row in pandasdf.iterrows():
    if row["ReqStatus"].lower() == "open" or row["ReqStatus"].lower() == "in_progress" or row["ReqStatus"] == "Frozen":
        yTestStartDates.append((row["StartDate"]-row["REQApprovalDate"]).days)
        pandasdf.loc[index, "StartDate"] = None

nameList = []
for index, row in pandasdf.iterrows():
    if row["HiringManagerId"] == "On Leave" and row["HiringManagerName"] not in nameList:
        nameList.append(row["HiringManagerName"])
idDict = {}
for index, row in pandasdf.iterrows():
    if row["HiringManagerName"] in nameList and row["HiringManagerId"].lower() != "on leave":
        idDict[row["HiringManagerName"]] = row["HiringManagerId"]
for index, row in pandasdf.iterrows():
    if row["HiringManagerName"] in idDict.keys() and row["HiringManagerId"].lower() == "on leave":
        row["HiringManagerId"] = idDict.get(str(row["HiringManagerName"]))

createYearList = []
createMonthList = []
createDayList = []
startYearList = []
startMonthList = []
startDayList = []
for index, row in pandasdf.iterrows():
    createYearList.append(row["REQApprovalDate"].year)
    createMonthList.append(row["REQApprovalDate"].month)
    #createDayList.append(row["REQApprovalDate"].day)
    startYearList.append(row["StartDate"].year)
    startMonthList.append(row["StartDate"].month)
    #startDayList.append(row["StartDate"].day)
pandasdf.insert(pandasdf.shape[1], "creation year", createYearList)
pandasdf.insert(pandasdf.shape[1], "creation month", createMonthList)
#pandasdf.insert(pandasdf.shape[1], "creation day", createDayList)
pandasdf.insert(pandasdf.shape[1], "start year", startYearList)
pandasdf.insert(pandasdf.shape[1], "start month", startMonthList)
#pandasdf.insert(pandasdf.shape[1], "start day", startDayList)

if runTimeBool == True:
    checkpoint = round(time.time()-start, 2)
    print(f"Editing conversion Runtime: {checkpoint}")

reqMasterIDList = []
removeReqMasterId = True
if removeReqMasterId == True:
    reqMasterIDList  = pandasdf["ReqMasterId"].tolist()
    pandasdf.drop("ReqMasterId", axis=1)

bookmarkdf = pandasdf.drop(pandasdf[pandasdf["ReqStatus"]=="Open"].index)
bookmarkdf = bookmarkdf.drop(bookmarkdf[bookmarkdf["ReqStatus"]=="Frozen"].index)
bookmarkdf = bookmarkdf.drop(bookmarkdf[bookmarkdf["ReqStatus"]=="In_Progress"].index)

oheBool = True
if oheBool == True:
    ohe = OneHotEncoder()
    #pandasdf["start year"] = (pandasdf["start year"].astype("category")).cat.codes
    #pandasdf["start month"] = (pandasdf["start month"].astype("category")).cat.codes
    #pandasdf["ReqStatus"] = (pandasdf["ReqStatus"].astype("category")).cat.codes
    pandasdf["creation month"] = (pandasdf["creation month"].astype("category")).cat.codes
    pandasdf["HiringManagerId"] = (pandasdf["HiringManagerId"].astype("category")).cat.codes
    pandasdf["CostCenter"] = (pandasdf["CostCenter"].astype("category")).cat.codes
    pandasdf["City"] = (pandasdf["City"].astype("category")).cat.codes
    pandasdf["Country"] = (pandasdf["Country"].astype("category")).cat.codes
    #pandasdf["JobFamily"] = (pandasdf["JobFamily"].astype("category")).cat.codes
    pandasdf["JobCode"] = (pandasdf["JobCode"].astype("category")).cat.codes

    ohearray = pd.DataFrame(ohe.fit_transform(pandasdf[[#"creation month", #"ReqStatus",
            "HiringManagerId", "CostCenter", "City",
            "Country", "JobCode"]]).toarray())
    pandasdf = pandasdf.join(ohearray)
    pandasdf = pandasdf.drop(["creation month", #"start month", #"ReqStatus",
            "HiringManagerName", "NbofReqs", "HiringManagerId", "CostCenter", "City",
            "Country", "JobCode"], axis=1)

if runTimeBool == True:
    checkpoint = round(time.time()-start, 2)
    print(f"Encoding runtime: {checkpoint}")

testData = pandasdf[pandasdf.StartDate.isnull()].reset_index(drop=True)
testData.insert(testData.shape[1], "Age", yTestStartDates)
ageList = []
for index, row in pandasdf.iterrows():
    age = (row["StartDate"] - row["REQApprovalDate"]).days
    if age >= 0:
        ageList.append(age)
    else:
        pandasdf = pandasdf.drop(index=index)
pandasdf.insert(pandasdf.shape[1], "Age", ageList)
pandasdf = pandasdf.dropna(axis=0, subset=["StartDate"])
pandasdf = pandasdf.reset_index(drop=True)

bucketList = []
if pandasdf["Age"].max() > testData["Age"].max():
    for i in range(0, pandasdf["Age"].max()+15, 15):
        bucketList.append(i)
else:
    for i in range(0, testData["Age"].max()+15, 15):
        bucketList.append(i)

pandasdf["AgeGroups"] = pd.cut(pandasdf["Age"], bucketList, include_lowest=True)
testData["AgeGroups"] = pd.cut(testData["Age"], bucketList, include_lowest=True)

if runTimeBool == True:
    checkpoint = round(time.time()-start, 2)
    print(f"Age Calculation Runtime {checkpoint}")

xaxis = pandasdf.drop(["start month", "creation year",
    "Age", "JobFamily", "AgeGroups", "StartDate", "start year", "REQApprovalDate", "ReqStatus"], axis=1)
yaxis = pandasdf["AgeGroups"]
xtest = testData.drop(["start month", "creation year",
    "Age", "JobFamily", "AgeGroups", "StartDate", "start year", "REQApprovalDate", "ReqStatus"], axis=1)
ytest = testData["AgeGroups"]

if oheBool == True:
    xtest.columns = xtest.columns.astype(str)
    xaxis.columns = xaxis.columns.astype(str)

exportAxisAndTest = True
if exportAxisAndTest == True:
    bookmarkdf.to_csv("bookmarked.csv", index=False, encoding="utf-8")
    xaxis.to_csv("xaxis.csv", index=False, encoding="utf-8")
    xtest.to_csv("xtest.csv", index=False, encoding="utf-8")
    yaxis.to_csv("yaxis.csv", index=False, encoding="utf-8")
    ytest.to_csv("ytest.csv", index=False, encoding="utf-8")
    
    if runTimeBool == True:
        checkpoint = round(time.time()-start, 2)
        print(f"Export Test and Axis: {checkpoint}\n")

print("Finish")
