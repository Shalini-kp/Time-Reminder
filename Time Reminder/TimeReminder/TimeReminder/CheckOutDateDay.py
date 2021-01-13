#!/usr/bin/python3
#CheckOut, considering both date and days

import datetime
import pandas as pd
from sklearn import linear_model

#Attendance_Report currentAttendance From1JanTo1Oct AttendanceForSeptember demoFrom1JanTo1Oct demoReport
#fileToParse = input("Enter the file name you want to parse: ")
userName = input("Enter the user name: ")

#parsing the file
df = pd.read_excel("/Users/TalentBridge/Desktop/TimeReminder/TimeReminder/Attendance" + ".xlsx")
df = df[df["Emp Name"] == userName]

#Name
df = df[pd.notnull(df['Emp Name'])]
name = df["Emp Name"]
f = df["Emp Name"][:1].to_string()

#Total hours
totalhours = input("Mention the total hours: ")

#UTC to Indian timezone
def UtcToIndianTime(utcTime, timeType):
    for index,i in utcTime.items():
        convertedTime = datetime.datetime.strptime(i, '%H:%M') + datetime.timedelta(hours=int(5)) + datetime.timedelta(minutes=int(30))
        
        if timeType == "checkIN":
            df["In Time( Asia/Calcutta )"][index] = convertedTime.time().strftime('%H:%M')
        else:
            df["Out Time(Asia/Calcutta )"][index] = convertedTime.time().strftime('%H:%M')
    
#CheckOut UTC to Indian TimeZone
df = df[pd.notnull(df['Out Time(Asia/Calcutta )'])]
#df = df[df["Checkout Type"] == "By User"]
utcCheckOut = df[df["Checkout Type"] == "By User"]
#UtcToIndianTime(utcCheckOut["Out Time"], "checkOut")

#CheckIn UTC to Indian TimeZone
df = df[pd.notnull(df['In Time( Asia/Calcutta )'])]
#UtcToIndianTime(df["In Time"], "checkIN")

#Date
df = df[pd.notnull(df['Attendance Date'])]
check_date = pd.to_datetime(df["Attendance Date"], format='%d-%m-%Y')
check_date = check_date.map(datetime.datetime.toordinal)

#Days
check_days = [datetime.datetime.strptime(s, '%d-%m-%Y').strftime('%u') for s in df["Attendance Date"]]    
check_days = pd.Series(check_days)


#checking user late check out
def roundedCheckOutTime(checkOutLate):
    for index, i in checkOutLate.iterrows():
        checkIntime = i["In Time( Asia/Calcutta )"]
        checkOuttime = datetime.datetime.strptime(checkIntime, '%H:%M') + datetime.timedelta(hours=int(totalhours))
        maxtime = pd.to_datetime('23:59', format='%H:%M')
    
        if checkOuttime < maxtime:
            df["Out Time(Asia/Calcutta )"][index] = checkOuttime.time().strftime('%H:%M')
        else:
            df["Out Time(Asia/Calcutta )"][index] = maxtime.time().strftime('%H:%M')
        
#Optimised checkOut values
roundedCheckOutTime(df[df["Checkout Type"] == "By User(late)"])
roundedCheckOutTime(df[df["Checkout Type"] == "Auto Check Out"])
    
#Check Out
checkOutTime = [datetime.datetime.strptime(s, '%H:%M').time() for s in df["Out Time(Asia/Calcutta )"]]
checkOutTime = map(lambda i: float('%s.%s' % (i.hour, i.minute)), checkOutTime)
checkOutTime = pd.Series(checkOutTime)

#create new dataframe
dic = {"Date" : pd.Series(check_date),"Day" : pd.Series(check_days),"Time" : pd.Series(checkOutTime)}
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
    print("\nCheckOut time =>", datetime.timedelta(hours=i))
    

from matplotlib import pyplot
#Graphical representation of Check Out
checkDays = [datetime.datetime.strptime(s, '%d-%m-%Y').strftime('%A') for s in df["Attendance Date"]]
testDays = [datetime.datetime.strptime(s, '%d-%m-%Y').strftime('%A') for s in test_Day]

pyplot.scatter(check_date, y, color='black')
pyplot.plot_date(testDate, predictions, color='red', linewidth=2)
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
    pyplot.title("Check Out =>  " + f[4] + " " + f[5] + " " + f[6])
elif len(f) == 6:
    pyplot.title("Check Out =>  " + f[4] + " " + f[5])
else:
    pyplot.title("Check Out =>  " + f[4])

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