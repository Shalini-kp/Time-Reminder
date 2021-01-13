#!/usr/source bin/python3
#CheckIn, considering both date and days

import datetime
import pandas as pd
from sklearn import linear_model

#Attendance_Report demoReport currentAttendance From1JanTo1Oct AttendanceForSeptember
#fileToParse = input("Enter the file name you want to parse: ")
userName = input("Enter the user name: ")

#parsing the file
df = pd.read_excel("/Users/TalentBridge/Desktop/TimeReminder/TimeReminder/Attendance" + ".xlsx")
df = df[df["Emp Name"] == userName]

#Check In
df = df[pd.notnull(df['In Time( Asia/Calcutta )'])]

#UTC to Indian TimeZone
# for index,i in df["In Time( Asia/Calcutta )"].items():
#     convertedTime = datetime.datetime.strptime(i, '%H:%M') + datetime.timedelta(hours=int(5)) + datetime.timedelta(minutes=int(30))
#     df["In Time( Asia/Calcutta )"][index] = convertedTime.time().strftime('%H:%M')

checkInTime = [datetime.datetime.strptime(s, '%H:%M').time() for s in df["In Time( Asia/Calcutta )"]]
checkInTime = map(lambda i: float('%s.%s' % (i.hour, i.minute)), checkInTime)
checkInTime = pd.Series(checkInTime)

#Name
df = df[pd.notnull(df['Emp Name'])]
name = df["Emp Name"]
f = df["Emp Name"][:1].to_string()

#Date
df = df[pd.notnull(df['Attendance Date'])]
check_date = pd.to_datetime(df["Attendance Date"], format='%d-%m-%Y')
check_date = check_date.map(datetime.datetime.toordinal)

#Days
check_days = [datetime.datetime.strptime(s, '%d-%m-%Y').strftime('%u') for s in df["Attendance Date"]]    
check_days = pd.Series(check_days)

#create new dataframe
dic = {"Date" : pd.Series(check_date),"Day" : check_days,"Time" : pd.Series(checkInTime)}
df2 = pd.DataFrame(dic)
df2 = df2.apply(lambda x: pd.Series(x.dropna().values))

x = df2[["Date","Day"]]
y = df2.Time

#Linear regression
lr = linear_model.LinearRegression()

#train the model
lr.fit(x, y)

#preparing test data
testDataDate = input("To predict the time please provide the date in d-m-yformat: ")
testDate = pd.to_datetime([testDataDate], format='%d-%m-%Y')
testDate = testDate.map(datetime.datetime.toordinal)

test_Day = pd.Series([testDataDate], dtype='str')
testDay = [datetime.datetime.strptime(s, '%d-%m-%Y').strftime('%u') for s in test_Day]
testDate = pd.Series(testDate)
testDay = pd.Series(testDay)

testDict = {"Date" : testDate,"Day" : testDay}
testDF = pd.DataFrame(testDict)
testDF = testDF.apply(lambda x: pd.Series(x.dropna().values))

testData = testDF[["Date","Day"]]

#predicting the time
predictions = lr.predict(testData)

for i in predictions:
    print("\nCheckIn time =>", str(datetime.timedelta(hours=i)))


from matplotlib import pyplot

#Graphical representation of Check In
checkDays = [datetime.datetime.strptime(s, '%d-%m-%Y').strftime('%A') for s in df["Attendance Date"]]
testDays = [datetime.datetime.strptime(s, '%d-%m-%Y').strftime('%A') for s in test_Day]

pyplot.scatter(check_date, y, color='black')
pyplot.plot_date(testDate, predictions, color='green', linewidth=2)
pyplot.xlabel("Date")
pyplot.ylabel("Time in hours")
pyplot.gcf().autofmt_xdate()
pyplot.grid()

#calculate Score, Coefficient and intercept
score = lr.score(testData, predictions)
coef = lr.coef_
inter = lr.intercept_

f = f.split(" ")

if len(f) == 7:
    pyplot.title("Check In =>  " + f[4] + " " + f[5] + " " + f[6])
elif len(f) == 6:
    pyplot.title("Check In =>  " + f[4] + " " + f[5])
else:
    pyplot.title("Check In =>  " + f[4])

pyplot.show()

#plotting 3D graph
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = (8.0, 5.0)
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter(df2.Date, df2.Day, df2.Time, color='red')
ax.scatter(testData.Date, testData.Day, predictions, color='green')
ax.set_xlabel('Date')
ax.set_ylabel('Days')
ax.set_zlabel('Time')
plt.show()

# save the model to disk
'''
from sklearn.externals import joblib
filename = 'finalized_model.sav'
joblib.dump(lr, filename)
 
# some time later...
 
# load the model from disk
loaded_model = joblib.load(filename)'''
# Encoding Categorial values
'''from sklearn.preprocessing import OneHotEncoder
labelencoder = LabelEncoder()
X[:, 0] = labelencoder.fit_transform(X[:, 0])
onehotencoder = OneHotEncoder(categorical_features = [0])
X = onehotencoder.fit_transform(np.array(check_days).reshape(-1, 1)).toarray()
print(X)'''