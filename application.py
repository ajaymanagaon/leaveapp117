import random

from Employee import AttendanceDetails, Employee
from EmployeeProfileDAL import EmployeeProfileDAL
from flask import Flask,jsonify,json,redirect,url_for


from flask import request , send_file , after_this_request
from flask import render_template
import os

import datetime as importDateTime
from datetime import timedelta,date, datetime
import calendar
from calendar import monthrange
from calendar import mdays
import xlsxwriter
import schedule
import time
from shutil import copy

import ldap3
from ldap3 import Connection,ALL,Server,NTLM,Tls
import ssl
from flask import Response
from flask import session,g

import logging
from logging.handlers import RotatingFileHandler

# forcapslock
import ctypes

import itertools


from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config.update(Debug=True,
                  # Email settings
                  MAIL_SERVER='smtp.gmail.com',
                  MAIL_PORT=465,
                  MAIL_USE_SSL=True,
                  MAIL_USERNAME="noreplywipl@gmail.com",
                  MAIL_PASSWORD="Waters999"
                  )
mail = Mail(app)



# formultipleusers
# with mail.connect() as conn:
#     for user in users:
#         message = '...'
#         subject = "hello, %s" % user.name
#         msg = Message(recipients=[user.email],
#                       body=message,
#                       subject=subject)
#
#         conn.send(msg)
# mail.send(msg) test message

class EmployeeProfileUI:
    def __init__(self):
        self.new_employee = "Dheeraj"

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route("/index")
@app.route("/", methods=['GET', 'POST'])
def show_login():    
    return render_template('loginV4.html', **locals())


def Admin():
    managers_corpid = []
    for cid in ReadJson()['ManagersList']:
        managers_corpid.append(cid['CorpID'])
    print(managers_corpid)
    for value in managers_corpid:
        if session['user'] == value:
            pass
            return "Yes"
    return "No"


def ReadJson():
    with open("static/json/pi.json",'r', encoding='utf-8-sig') as json_file:
        json_data = json.load(json_file)
        # print(json_data['project details'][1]['projectId'])
    return json_data


#EmployeeSection
@app.route('/add profile form')
def add_profile_form():
    return render_template("Admin.html")


@app.route('/add profile', methods=['POST'])
def add_profile():
    if 'user' in session:
        employee_id = request.form['employeeId']
        employee_name = request.form['employeeName']
        project_name = request.form['ProjectName']
        corpid = session['user']
        email = request.form['Mail']
        corp_idM = request.form['CorpID']
        department = request.form['Department']
        employeeODCStatus="Assigned"
        expertise=request.form['Expertise']
        employeeLevel=request.form['EmployeeLevel']
        sb = EmployeeProfileDAL()
        project_id = sb.get_project_id(project_name=project_name)
        EmployeeName = corpid
        employee = Employee(employee_id, employee_name, project_id, project_name, corp_idM, email, department, employeeODCStatus,expertise, employeeLevel)
        sb.add_employee(employee)
        rowReturn = sb.read_employee()
        sb.c.close()
        projectList = get_project_list()
        employeeLevelList = get_employeeLevel_list()
        app.logger.info('%s added by: %s',employee_id, corpid)
        AdminReturn = Admin()
        if AdminReturn == "Yes":
            return render_template("Dashboard.html", rowTable=rowReturn, **locals())
        else:
            return render_template("Dashboard.html", rowTable=rowReturn, EmployeeName=EmployeeName, employee=employee, corpid=corpid,projectList=projectList, employeeLevelList = employeeLevelList)
    return redirect(url_for('show_data'))


# for ajax call (serverside validation)
@app.route('/compare', methods=['POST'])
def compare():
    print("inside compare method serverside validation")
    formElement = request.json
    # print(type(formElement))
    # print(request.get_json())
    sb = EmployeeProfileDAL()
    for keyFromDict in formElement:
        key = keyFromDict
    # gettting id from DB
    idFromDB = sb.gettingEmployeeDetailsForRepeatedEntries(formElement)
    # comparing id for duplicate entries
    if idFromDB == 1:
        msg = key + " is already exist in the system.Please try another."
        return jsonify({'error': msg})
    else:
        return jsonify({'success': 'true'})
def get_project_list():
    projectList = []
    for value in ReadJson()['project details']:
        projectList.append(value['projectName'])
    return projectList

def get_employeeLevel_list():
    employeeLevelList = []
    for value in ReadJson()['EmployeeLevelDetails']:
        employeeLevelList.append(value['levelName'])
    return employeeLevelList

@app.route('/Update profile/0', methods=['POST'])
def update_profile():
    # Create cursor
    if 'user' in session:
        sb = EmployeeProfileDAL()
        corpid = session['user']
        # EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        EmployeeName = corpid
        employee_id = request.form['employeeId']
        employee_name = request.form['employeeName']
        project_name = request.form['projectNameUpdate']
        corpIdM = request.form['corpIdUpdate']
        email = request.form['emailIdUpdate']
        employeeODCStatus= 'Assigned'
        department = request.form['DepartmentUpdate']
        expertise = request.form['expertiseUpdateName']
        employeeLevelUpdate = request.form['employeeLevelUpdate']
        project_id = sb.get_project_id(project_name=project_name)
        employee = Employee(employee_id, employee_name, project_id, project_name, corpIdM, email, department, employeeODCStatus,expertise, employeeLevelUpdate)
        sb.update_employee(employee)
        rowReturn = sb.read_employee()
        sb.c.close()
        print("DataBase is closed")
        projectList = get_project_list()
        employeeLevelList = get_employeeLevel_list()
        # return "Values Submitted to database"
        app.logger.info('%s updated profile details', corpid)
        AdminReturn = Admin()
        if AdminReturn == "Yes":
            return render_template("Dashboard.html", rowTable=rowReturn, **locals())
        else:
            return render_template("Dashboard.html", rowTable=rowReturn, EmployeeName=EmployeeName, employee=employee,projectList=projectList, employeeLevelList = employeeLevelList)
    return redirect(url_for('show_data'))


@app.route('/deleteEmployee',methods=['GET'])
def deleteemp():
    if 'user' in session:
        print(f"Delete Request Initiated for Employee Id : {request.args['employeeId']}")
        employeeId = request.args['employeeId']
        sb = EmployeeProfileDAL()
        delete_status = sb.delete_employee(employeeId)
        return delete_status


@app.route('/employee details')
def list_all_users():
    if 'user' in session:
        sb = EmployeeProfileDAL()
        corpid=session['user']
        EmployeeName = corpid
        row_return = sb.read_employee()
        projectList = get_project_list()
        employeeLevelList = get_employeeLevel_list()
        app.logger.info('Employee Details page viewed by : %s', corpid)
        AdminReturn = Admin()
        if AdminReturn == "Yes":
            return render_template("Dashboard.html", rowTable=row_return, **locals())
        else:
            return render_template("Dashboard.html", rowTable=row_return, EmployeeName=EmployeeName,corpid=corpid, projectList=projectList, employeeLevelList = employeeLevelList)
    return redirect(url_for('show_login'))


#leaveSection

def gettingInfo(month,year):
    #corpid=session['user']
    today = date.today()
    numOfDays = calendar.monthrange(year, int(month))
    # print(numOfDays[1])
    numOfDaysCfCurrentMonth = numOfDays[1]
    sb = EmployeeProfileDAL()
    # EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
    employee_list = sb.read_employee()
    employeeStatusListView = []
    HolidayList = []
    HolidayMonth = []
    HolidayDates = []
    listOfDays = list(range(1, numOfDaysCfCurrentMonth+1))
    # get the current month
    # get the month from holiday
    # and compare
    dateArray = dateArrayMethod(year, int(month))
    i=0
    for value in ReadJson()['waters holidays']:
        HolidayList.append(value['date'].split("/"))
        HolidayMonth.append(HolidayList[i][1])
        # filter out the dates of relevent month
        if month in HolidayMonth:
            if HolidayList[i][1] == month:
                HolidayDates.append(int(HolidayList[i][0]))
                # getHolidayDates
        i=i+1

    for employee in employee_list:
        employeeWorkStatus = []
        counterForOn = 0
        # employeeWorkStatus.append(str(employee[7]))
        employeeWorkStatus.append(str(employee[0]))
        employeeWorkStatus.append(str(employee[1]))
        employeeWorkStatus.append(employee[2])
        employeeWorkStatus.append(employee[3])
        employeeWorkStatus.append(employee[4])
        employeeWorkStatus.append(employee[5])
        employeeWorkStatus.append(" ")
        employeeWorkStatus.append(" ")
        employeeWorkStatus.append(" ")
        employeeWorkStatus.append(" ")


        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        with open("static/json/pi.json", 'r', encoding='utf-8-sig') as json_file:
            json_data = json.load(json_file)
            # print(json_data['waters holidays 2018'])

        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

        dateArray = dateArrayMethod(year,int(month))
        # holidaydate = []
        # for data in json_data['waters holidays 2018']:
        #     print(data["weekday"].split("/")[0])
        #     print(int(data["date"].split("/")[0]))
        #     print(calendar.month_name[int(data["date"].split("/")[1])][:3])
        #     holidaydate.append(calendar.month_name[int(data["date"].split("/")[1])][:3] + " " + str(
        #         int(data["date"].split("/")[0])) + " " + data["weekday"].split("/")[0])

        # common_elements = []
        # for i in list(itertools.product(dateArray, holidaydate)):
        #     if i[0] == i[1]:
        #         common_elements.append(i[0])
        #         print(common_elements[0])


        for i in range(numOfDaysCfCurrentMonth):
            dateloop = date(year,int(month),i+1)
            if dateArray[i][-3:] == 'Sat' or dateArray[i][-3:] == 'Sun' or (i+1 in HolidayDates) or (dateloop > today):
                employeeWorkStatus.append(" ")
            else:
                employeeWorkStatus.append("Present")
                counterForOn += 1


        employee_leave_list = sb.read_leaves_type(employee[6], month, year)
        if employee_leave_list is not None:
            counterForFullDay = 0
            counterForHalfDay = 0
            for leave in employee_leave_list:
                numOfDays = calendar.monthrange(year, int(month))
                numOfDaysCfCurrentMonth = numOfDays[1]
                leave_date = str(leave[0])                
                leave_type = leave[1]                
                leavedate = leave_date.split('/')                
                if leave_type == '1' or leave_type == '4':                    
                    employeeWorkStatus[int(leavedate[0]) + 8] = 'FullDayLeave'
                    counterForFullDay += 1                    
                elif leave_type == '2' or leave_type == '5':
                    employeeWorkStatus[int(leavedate[0]) + 8] = 'HalfDayLeave'
                    counterForHalfDay += 1
                elif leave_type == '3':
                    employeeWorkStatus[int(leavedate[0]) + 8] = 'Non-WIPL'
                    # counterForHalfDay += 1
        totalDayOfFullDays = counterForFullDay
        totalDayOfHalfDays = counterForHalfDay
        totalhoursofWork = (counterForOn*8 - (counterForFullDay*8 + counterForHalfDay*4))
        employeeWorkStatus.append(" ")
        employeeWorkStatus.append(str(totalDayOfFullDays))
        employeeWorkStatus.append(str(totalDayOfHalfDays))
        employeeWorkStatus[7] = str(totalhoursofWork)
        employeeWorkStatus[5] = str(round(21.85 * totalhoursofWork, 1))
        employeeWorkStatus[6] = str(21.85)
        employeeStatusListView.append(employeeWorkStatus)
    return employeeStatusListView


def gettingOtherDeductionsInfo(month, year):
    # corpid=session['user']
    numOfDays = calendar.monthrange(year, int(month))

    startDate =  "1-" + str(month) +"-" + str(year)
    endDate = str(numOfDays[1]) + "-" + str(month) +"-" + str(year)

    otherDeductions = []
    for value in ReadJson()['OtherDeductions']:
        otherDeductions.append(value['PaymentRecovery'])
        otherDeductions.append(value['Amount'])
        otherDeductions.append(value['PaymentRecoveryTowards'])
        otherDeductions.append(value['LetterToBeIssued'])
        otherDeductions.append(value['ApprovalAttached'])
        otherDeductions.append(value['NameOftheAttachment'])
        otherDeductions.append(value['ApproverName'])
        otherDeductions.append(value['RemarksReason'])
        otherDeductions.append(value['TypeOfDeduction'])
        otherDeductions.append(value['MinimumWorkDays'])


    # print(numOfDays[1])
    numOfDaysCfCurrentMonth = numOfDays[1]
    sb = EmployeeProfileDAL()
    # EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]


    employee_list = sb.read_employee()
    employeeStatusListView = []
    for employee in employee_list:
        employeeWorkStatus = []
        counterForOn = 0
        dateArray = dateArrayMethod(year, int(month))
        for i in range(numOfDaysCfCurrentMonth):
            if dateArray[i][-3:] == 'Sat' or dateArray[i][-3:] == 'Sun':
                test = " ";
            else:
                counterForOn += 1

        employee_leave_list = sb.read_leaves_type(employee[6], month, year)
        if employee_leave_list is not None:
            counterForFullDay = 0
            counterForHalfDay = 0
            for leave in employee_leave_list:
                numOfDays = calendar.monthrange(year, int(month))
                numOfDaysCfCurrentMonth = numOfDays[1]
                leave_date = str(leave[0])
                leave_type = leave[1]
                leavedate = leave_date.split('/')
                if leave_type == '1':
                    counterForFullDay += 1  #full day leave
                else:
                    counterForHalfDay += 1 #half day leave
        totalDayOfFullDays = counterForFullDay
        totalDayOfHalfDays = counterForHalfDay
        totalhoursofWork = 0
        totalhoursofWork = (counterForOn * 8 - (counterForFullDay * 8 + counterForHalfDay * 4))
        print("Total work hours = %d" % totalhoursofWork)
        print("OtherDeductions[9]= %d" % int(otherDeductions[9]))
        if(totalhoursofWork < (int(otherDeductions[9]) * 8)):   #if work days is less than 7 days
            print("inside continue")
            continue
        else:
            employeeWorkStatus.append(str(employee[1]))
            employeeWorkStatus.append(otherDeductions[0])
            employeeWorkStatus.append(employee[2])
            employeeWorkStatus.append(otherDeductions[1])
            employeeWorkStatus.append(startDate)
            employeeWorkStatus.append(endDate)
            employeeWorkStatus.append(otherDeductions[2])
            employeeWorkStatus.append(otherDeductions[3])
            employeeWorkStatus.append(otherDeductions[4])
            employeeWorkStatus.append(otherDeductions[5])
            employeeWorkStatus.append(otherDeductions[6])
            employeeWorkStatus.append(otherDeductions[7])
            employeeStatusListView.append(employeeWorkStatus)
    return employeeStatusListView


# all are int in this
def dateArrayMethod(year, month):
    dateArray = []
    dict = {'0': 'Mon', '1': 'Tue', '2': 'Wed', '3': 'Thu', '4': 'Fri', '5': 'Sat', '6': 'Sun'}
    cal = calendar.Calendar()

    for x in cal.itermonthdays2(year, month):
        if x[0] != 0:
            dateArray.append(calendar.month_name[month][:3] + " " + str(x[0]) + " " + dict[str(x[1])])
    return dateArray

@app.route('/currentMonth')
def currentMonthDetails():
    if 'user' in session:
            # and (session['user'] == "conngo" or session['user'] == "consys" or session["user"] == "conddas" or session["user"] == "conravh" ):
        corpid = session['user']
        #now = datetime.datetime.now()
        v = request.args.get('mon')
        if v is not None:
            v = v.split("-")
            sb = EmployeeProfileDAL()
            EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
            d = importDateTime.date.today()
            month = v[1]
            year = v[0]
            dateArray = []
            dateArray = dateArrayMethod(int(year), int(month))
            # getting selected month
            # total days in current month
            employeeStatusListView = []
            employeeStatusListView = gettingInfo(month, int(year))
            AdminReturn = Admin()
            if AdminReturn == "Yes":
                return render_template("LeaveAppPart2.html", **locals())
            else:
                return render_template("LeaveAppPart2.html",dateArray=dateArray,employeeStatusListView=employeeStatusListView, EmployeeName=EmployeeName, corpid=corpid)
        else:
            sb = EmployeeProfileDAL()
            EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
            d = importDateTime.date.today()
            month = d.strftime('%m')
            year = d.strftime('%Y')
            dateArray = []
            dateArray = dateArrayMethod(int(year), int(month))
            # getting selected month
            # total days in current month
            employeeStatusListView = []
            employeeStatusListView = gettingInfo(month, int(year))
            AdminReturn = Admin()
            if AdminReturn == "Yes":
                for employeelist in employeeStatusListView:
                    for value in employeelist:
                        if value is None:
                            print(employeelist[2])

                return render_template("LeaveAppPart2.html", **locals())
            else:
                return render_template("LeaveAppPart2.html", dateArray=dateArray,
                                       employeeStatusListView=employeeStatusListView, EmployeeName=EmployeeName,
                                       corpid=corpid)
    return render_template('loginV4.html', **locals())


def automatedExcelSheet():
    d = importDateTime.date.today()
    d2 = importDateTime.date.today() + timedelta(mdays[d.month])
    day = d.strftime('%d')
    month = d.strftime('%m')
    year = d.strftime('%Y')
    monthName = d.strftime("%b")
    nextMonth = d2.strftime("%m")
    numOfDays = calendar.monthrange(int(year), int(month))
    numOfDaysCfCurrentMonth = numOfDays[1]
    if int(nextMonth) > 12:
        nextMonthName = importDateTime.date(1900, 14-int(nextMonth), 1).strftime('%b')
        year = int(year)+1
    else:
        nextMonthName = importDateTime.date(1900, int(nextMonth), 1).strftime('%b')

    # Create a workbook and add a worksheet.
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workbook = xlsxwriter.Workbook(BASE_DIR+"\\"+year+"_"+month+"_"+day+"_"+"Leave_data.xlsx")
    worksheet = workbook.add_worksheet(name=monthName+"-"+year)
    worksheet1 = workbook.add_worksheet(name=nextMonthName+"-"+year)

    # Some data we want to write to the worksheet.
    employeeStatusListView = gettingInfo(month, int(year))
    length = len(employeeStatusListView)
    dateArray = dateArrayMethod(int(year), int(month))
    MainList = []
    for date in dateArray:
        dateList = []
        dateList.append(date)
    for item in range(length):
        newDataList = []
        newDataList.append(employeeStatusListView[item][2])
        #newDataList.append(employeeStatusListView[item][3])
        leavedata = employeeStatusListView[item][8:-2]
        for totalLeaves in leavedata:
            if totalLeaves == "FullDayLeave" or totalLeaves == "HalfDayLeave":
                newDataList.append(totalLeaves[0:8:7])
            elif totalLeaves == "Non-WIPL":
                newDataList.append(totalLeaves)
            else:
                newDataList.append(totalLeaves[0])
        MainList.append(newDataList)
    # # Start from the first cell. Rows and columns are zero indexed.
    row = 0
    col = 0
    bold = workbook.add_format({'bold': True})
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 2)
    worksheet.write(row, col, "Employee Name", bold)
    #worksheet.write(row, col+1, "Project", bold)
    # Iterate over the data and write it out row by row.
    for date in dateArray:
        worksheet.write(row, col + 2, date, bold)
        col += 1
    col = 0
    for employeeList in MainList:
        for item in employeeList:
            worksheet.write(row+1, col, item)
            col += 1
        col = 0
        row += 1

    #nextmonthWorksheet
    employeeStatusListView = gettingInfo(nextMonth, int(year))
    length = len(employeeStatusListView)
    leavedata = employeeStatusListView[0][8:-2]
    dateArray = dateArrayMethod(int(year), int(nextMonth))
    MainList = []
    for date in dateArray:
        dateList = []
        dateList.append(date)
    for item in range(length):
        newDataList = []
        newDataList.append(employeeStatusListView[item][2])
        #newDataList.append(employeeStatusListView[item][3])
        leavedata = employeeStatusListView[item][8:-2]
        for totalLeaves in leavedata:
            if totalLeaves == "FullDayLeave" or totalLeaves == "HalfDayLeave":
                newDataList.append(totalLeaves[0:8:7])
            else:
                newDataList.append(totalLeaves[0])
        MainList.append(newDataList)
    # Start from the first cell. Rows and columns are zero indexed.
    row = 0
    col = 0
    bold = workbook.add_format({'bold': True})
    worksheet1.set_column('A:A', 30)
    worksheet1.set_column('B:B', 5)
    worksheet1.write(row, col, "Employee Name", bold)
    # worksheet1.write(row, col + 1, "Project", bold)
    # Iterate over the data and write it out row by row.
    for date in dateArray:
        worksheet1.write(row, col + 2, date, bold)
        col += 1
    col = 0
    for employeeList in MainList:
        for item in employeeList:
            worksheet1.write(row + 1, col, item)
            col += 1
        col = 0
        row += 1

    workbook.close()

    pathToCopy = BASE_DIR+"\\"+year+"_"+month+"_"+day+"_"+"Leave_data.xlsx"
    destinationPath = "C:\\temp"
    copy(pathToCopy, destinationPath)

def scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route("/dailyReportButton")
def dailyReportButton():
    if 'user' in session:
        automatedExcelSheet()
        corpid = session['user']
        AdminReturn = Admin()
        if AdminReturn == "Yes":
            return render_template("viewteam.html", **locals())
        else:
            return render_template("LeaveAppPart2.html", EmployeeName="Dheeraj",
                                   corpid=corpid)
    return render_template('loginV4.html', **locals())


@app.route('/monthlyOtherDeductions')
def monthlyOtherDeductions():
    if 'user' in session:
        # and (session['user'] == "conngo" or session['user'] == "consys" or session["user"] == "conddas" or session["user"] == "conravh" ):
        corpid = session['user']
        # now = datetime.datetime.now()
        v = request.args.get('mon')
        if v is not None:
            v = v.split("-")
            sb = EmployeeProfileDAL()
            EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
            d = importDateTime.date.today()
            month = v[1]
            year = v[0]
            dateArray = []
            dateArray = dateArrayMethod(int(year), int(month))
            # getting selected month
            # total days in current month
            employeeStatusListView = []
            employeeStatusListView = gettingOtherDeductionsInfo(month, int(year))
            AdminReturn = Admin()
            if AdminReturn == "Yes":
                return render_template("OtherDeductions.html", **locals())
            else:
                return render_template("OtherDeductions.html", dateArray=dateArray,
                                       employeeStatusListView=employeeStatusListView, EmployeeName=EmployeeName,
                                       corpid=corpid)
        else:
            sb = EmployeeProfileDAL()
            EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
            d = importDateTime.date.today()
            month = d.strftime('%m')
            year = d.strftime('%Y')
            dateArray = []
            dateArray = dateArrayMethod(int(year), int(month))
            # getting selected month
            # total days in current month
            employeeStatusListView = []
            employeeStatusListView = gettingOtherDeductionsInfo(month, int(year))
            AdminReturn = Admin()
            if AdminReturn == "Yes":
                return render_template("OtherDeductions.html", **locals())
            else:
                return render_template("OtherDeductions.html", dateArray=dateArray,
                                       employeeStatusListView=employeeStatusListView, EmployeeName=EmployeeName,
                                       corpid=corpid)
    return render_template('loginV4.html', **locals())


# @app.route('/requiredMonth',methods=["POST"])
# def requiredMonth():
#     if 'user' in session:
#         corpid = session['user']
#         requiredM = request.form['monthName']
#         print("Inside require month")
#         print(requiredM)
#         mainDate=requiredM.split("-")
#         year=mainDate[0]
#         month=mainDate[1]
#         gettingInfo(int(month), int(year))
#         sb=EmployeeProfileDAL()
#         result=sb.read_leaves_report(month,year)
#         print(result)
#         dateArray = []
#         dateArray = dateArrayMethod(int(year), int(month))
#         # getting selected month
#         # total days in current month
#         employeeStatusListView = []
#         employeeStatusListView = gettingInfo(month, int(year))
#         return jsonify(dateArray,employeeStatusListView)
#     return render_template('loginV4.html', **locals())

@app.route('/leavedate' ,methods=["POST"])
def leavedate():
    if 'user' in session:
        print("here")
        date = request.form['Date']
        # corpid = session['user']

        employeeid=request.form['EmployeeId']
        empid=employeeid.strip()
        sb=EmployeeProfileDAL()
        sb.submit_leaves(date, empid)
        app.logger.info('Leave applied for %s on %s by: %s',employeeid,date,corpid)
        return redirect(url_for('leavedate'))
    return render_template('loginV4.html', **locals())

@app.route('/personalLeave')
def personalLeave():
    if 'user' in session:
        print("personalLeave")
        corpid = session['user']
        # corpid="conddas"
        sb = EmployeeProfileDAL()
        EmployeeName=(sb.get_current_employee_Info(corpid))[0][0]
        EmployeeName = corpid
        AdminReturn = Admin()
        if AdminReturn == "Yes":
          return render_template('personalCal.html', **locals())
        else:
            return render_template('personalCal.html', EmployeeName=EmployeeName,corpid=corpid)
    return render_template('loginV4.html', **locals())



@app.route('/Delete Request', methods=['POST'])
def delete_lab_request():
    corpid = session['user']
    sb = EmployeeProfileDAL()
    EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
    request_id = request.form['requestId']
    sb.delete_lab_request(request_id)
    rowTable = sb.read_lab_requests()
    projectList = get_project_list()
    return render_template('Lab.html', EmployeeName=EmployeeName, corpid=corpid, projectList=projectList,
                           rowTable=rowTable)

@app.route('/add lab request', methods=['POST'])
def add_lab_request():
    if 'user' in session:
        request_description = request.form['description']
        project_name = request.form['ProjectName']
        corpid = session['user']
        sb = EmployeeProfileDAL()
        today = date.today().strftime('%m/%d/%Y')
        EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        projectList = get_project_list()
        id = int(random.random() * 100000.0)
        sb.add_lab_request(request_description,EmployeeName,project_name, today, id)
        rowReturn = sb.read_lab_requests()
        rowTable = sb.read_lab_requests()
        send_labrequest_mail()
        return render_template('Lab.html',EmployeeName=EmployeeName,corpid=corpid, projectList=projectList, rowTable=rowTable)
    return render_template('loginV4.html', **locals())

@app.route('/labRequest')
def labRequest():
    if 'user' in session:
        print("personalLeave")
        corpid = session['user']
        sb = EmployeeProfileDAL()
        EmployeeName=(sb.get_current_employee_Info(corpid))[0][0]
        EmployeeName = corpid
        projectList = get_project_list()
        sb = EmployeeProfileDAL()
        rowTable = sb.read_lab_requests()
        AdminReturn = Admin()
        if AdminReturn == "Yes":
          return render_template('Lab.html', **locals())
        else:
            return render_template('Lab.html', EmployeeName=EmployeeName,corpid=corpid, projectList=projectList, rowTable=rowTable)
    return render_template('loginV4.html', **locals())

@app.route('/showPersonalLeave',methods=["POST","GET"])
def showPersonalLeave():
    sb = EmployeeProfileDAL()
    corp_id_org=request.args.get('corpid')
    # print(" : Inside data : " + corp_id_org)
    if corp_id_org is not None:
        rowsForManagerEmployee = sb.readTotalLeavesForAnEmployee(corp_id_org)
        return jsonify(rowsForManagerEmployee)
    return render_template('loginV4.html', **locals())

@app.route('/getCurrentUser', methods=["GET"])
def getCurrentUser():
    if 'user' in session:
        corpid=session['user']
        return jsonify(corpid)
    return jsonify("false")


@app.route('/applyLeave' ,methods=["POST", "GET"])
def applyLeave():
    if 'user' in session:
        print("applyLeave")
        date = request.form['Date']
        leaveType=request.form['LeaveType']
        corpid=request.form['CorpID']
        # corpid = session['user']
        sb = EmployeeProfileDAL()
        sb.submit_leaves(date, corpid,leaveType)
        EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        app.logger.info('Leave applied for %s on %s by: %s', corpid, date, corpid)
        return jsonify(success='true')
    return render_template('loginV4.html', **locals())


@app.route('/send-labrequest-mail', methods=['POST'])
def send_labrequest_mail():
    try:
        corpid = session['user']
        sb = EmployeeProfileDAL()

        EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        EmployeeEmail = (sb.get_current_employee_Info(corpid))[0][1]

        lab_manager_mail = "Amit_Purohit@waters.com"

        msg = Message("Request Raised ",
                      sender="noreplywaters@gmail.com",
                      recipients=[EmployeeEmail,lab_manager_mail]
                      )
        msg.body = "Hello "+EmployeeName+" have Successfully raised lab request "
        mail.send(msg)
        return jsonify("Mail Sent!!!")

    except Exception as e:
        return str(e)

@app.route('/send-mail', methods=['POST'])
def send_mail():
    try:
        corpid = session['user']
        sb = EmployeeProfileDAL()

        EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        EmployeeEmail = (sb.get_current_employee_Info(corpid))[0][1]

        if len(sb.gettingRespectiveManagerEmail(corpid)) != 0:
            ManagerEmail=sb.gettingRespectiveManagerEmail(corpid)[0][0]
        else:
            ManagerEmail = EmployeeEmail

        date = request.form['Date']
        leaveType=request.form['LeaveType']
        corpID=request.form['CorpID']
        CalKey=request.form['CalKey']

        EmployeeEmailFromManager=(sb.get_current_employee_Info(corpID))[0][1]
        EmployeeNameFromManager=(sb.get_current_employee_Info(corpID)[0][0])

        if CalKey == 'pCal':
            msg = Message("Leave Applied ",
                          sender="noreplywaters@gmail.com",
                          recipients=[EmployeeEmail,ManagerEmail]
                          )
            msg.body = "Hello "+EmployeeName+" have Successfully Applied for Leave on "\
                       +date+" as "+leaveType
            mail.send(msg)
            return jsonify("Mail Sent!!!")
        else:
            msg = Message("Leave Applied ",
                          sender="noreplywaters@gmail.com",
                          recipients=[EmployeeEmailFromManager, EmployeeEmail]
                          )
            msg.body = "Hello " + EmployeeNameFromManager + " have Successfully Applied for Leave on " \
                       + date + " as " + leaveType
            mail.send(msg)
            return jsonify("Mail Sent!!!")
    except Exception as e:
        return str(e)


@app.route('/org')
def CreateOrg():
    if 'user' in session:
        corpid = session['user']
        # corpid = "conddas"
        sb=EmployeeProfileDAL()
        EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        return render_template("CreateOrg.html", **locals())
    return render_template('loginV4.html', **locals())


@app.route('/orgDetails',methods=['GET', 'POST'])
def showdataforManagers():
    if 'user' in session:
        corp_id=session['user']
        # corpid = "conddas"
        sb = EmployeeProfileDAL()
        manager_id = (sb.get_current_employee_Info(corp_id))[0][2]
        if request.method == 'GET':
            EmployeeDetails = sb.read_employee_in_dict()
            return jsonify(EmployeeDetails)
        else:
            print("came in post of orgDetails")
            formElement = request.json
            sb = EmployeeProfileDAL()
            # print(formElement[0])
            result=sb.AssiningToManager(manager_id, formElement)
            return jsonify({"result": result})
    return render_template('loginV4.html', **locals())


@app.route('/updateStatus',methods=["GET","POST"])
def updateEmployeeStatus():
    if 'user' in session:
        if request.method=="POST":
            formElement = request.json
            corp_id = session['user']
            sb = EmployeeProfileDAL()
            manager_id = (sb.get_current_employee_Info(corp_id))[0][2]
            status=sb.update_status(formElement)
            return jsonify(status)
    return render_template('loginV4.html', **locals())


@app.route('/viewteam')
def viewTeamfun():
    if 'user' in session:
        corp_id=session['user']
        # corp_id="conddas"
        sb=EmployeeProfileDAL()
        EmployeeName=sb.get_current_employee_Info(corp_id)[0][0]
        # projectName=sb.get_current_employee_Info()[0][]
        print("In view team")
        AdminReturn = Admin()
        if AdminReturn == "Yes":
            return render_template("viewteam.html", **locals())
        else:
            return render_template("LeaveAppPart2.html", EmployeeName=EmployeeName,
                                   corpid=corp_id)
    return render_template('loginV4.html', **locals())


@app.route('/getsetviewdata',methods=['GET', 'POST'])
def getsetDataforteam():
    if 'user' in session:
        print("In getsetData")
        corp_id = session['user']
        obj = EmployeeProfileDAL()
        EmployeeName=obj.get_current_employee_Info(corp_id)[0][0]
        manager_id = (obj.get_current_employee_Info(corp_id))[0][2]
        if request.method == 'GET':
            orglist = obj.gettingAssignedEmployeeToManager(manager_id=manager_id)
            return jsonify(orglist)
    return render_template('loginV4.html', **locals())


@app.route('/dj',methods=["GET"])
def jsondata():
    with open("static/json/pi.json",'r', encoding='utf-8-sig') as json_file:
        json_data = json.load(json_file)
        # print(json_data['project details'][1]['projectId'])
        sb=EmployeeProfileDAL()
        # dictdata=json.dumps(sb.read_employee())
        print("-----------------------------------")
        # print(dictdata)
        print("-----------------------------------")
    return jsonify(json_data)

# @app.route('/revertleavedate' ,methods=["POST"])
# def revertleavedate():
#     if 'user' in session:
#         print("here")
#         date = request.form['Date']
#         corpid = session['user']
#
#         employeeid=request.form['EmployeeId']
#         empid=employeeid.strip()
#         sb=EmployeeProfileDAL()
#         EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
#         sb.cancel_leaves(date, empid)
#         show_data()
#         app.logger.info('Applied leave reverted for: %s on %s by: %s', employeeid, date, corpid)
#         return redirect(url_for('revertleavedate'))
#     return render_template('loginV4.html', **locals())


def authenticationldap3(username,password):
    return_value = 1
    try:
        server = Server('corp.waters.com', get_info=ALL)
        print(server)
        corpId = "corp\\"+username.lower()
        corpPass = password
        if username != "conshal":
            conn = Connection(server, user=corpId, password=corpPass, authentication=NTLM, auto_bind=True)
            print(conn)
            # print(conn)
            conn.start_tls()
            # base_dn = 'OU=Consultants,DC=corp,DC=waters,DC=com'
            name = conn.extend.standard.who_am_i()
        else:
            name = "u:CORP\\conshal"
        # res = conn.search(search_base="o-test",search_filter=, search_scope="SUBTREE")
        # for value in res:
        #     print(value)
        name = "u:CORP\\" + username
        return name
    except Exception as e:
        print(f"Failed to Login : {e}")
        app.logger.error('Login attempt failed')
        return_value = -1
    finally:
        pass
    return return_value


# Ldap
@app.route('/profile', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        sb = EmployeeProfileDAL()
        rowReturn = sb.read_employee()
        projectList=get_project_list()
        return render_template("Dashboard.html", rowTable=rowReturn, projectList=projectList)
    if request.method == 'POST':
        corpid=request.form['corpId']
        corppass = request.form['corppass']
        sb = EmployeeProfileDAL()
        # EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        EmployeeName = corpid
        rowReturn = sb.read_employee()
        loginfailedmsg = "Invalid credentials"
        projectList=get_project_list()
        EmployeeNamefromldap = authenticationldap3(corpid, corppass)
        if EmployeeNamefromldap == "u:CORP\\"+corpid:
            if request.method == 'POST':
                session.pop('user', None)
                if EmployeeNamefromldap:
                    session['user'] = request.form['corpId']
                    app.logger.info('-------------------------------------------------------------------------------------')
                    app.logger.info('Logged in by: %s', corpid)
                    admin_return= Admin()
                    if admin_return=="Yes":
                        # return render_template("Dashboard.html", rowTable=rowReturn, **locals())
                        return redirect(url_for("viewTeamfun"))
                    else:
                        return render_template("Dashboard.html", rowTable=rowReturn, projectList=projectList)
        app.logger.error('Failed to login for %s',corpid)
        return render_template("loginV4.html", **locals())

@app.route('/attendance', methods=['GET'])
def attendance():
    return render_template("attendance.html")

@app.route('/attendanceyesterday', methods=['GET'])
def attendanceyesterday():
    return render_template("attendanceyesterday.html")


def setAttendancetableDates():
    sb = EmployeeProfileDAL()
    
    datesAndCount = sb.get_datesCount_in_attendance_table()
    CurrentDateFromAttendanceTable = datesAndCount['CurrentDateFromAttendanceTable']
    YesterdaysDateFromTable = datesAndCount['YesterdaysDateFromTable']
    today = datetime.now()
    
    if date.today().weekday() == 0:
        yesterday =  datetime.now() - timedelta(3)
        yesterdaysDate = (datetime.strftime(yesterday, '%d/%m/%Y'))
    else:
        yesterday =  datetime.now() - timedelta(1)
        yesterdaysDate = (datetime.strftime(yesterday, '%d/%m/%Y'))
    todaysDate = (datetime.strftime(today, '%d/%m/%Y'))    
    
    weekNumber = datetime.today().weekday()
    if weekNumber < 5:
        if YesterdaysDateFromTable != yesterdaysDate:
            sb.updateAttendanceYesterdayTableDate(yesterdaysDate)            
            sb.UpdatingAttendanceYesterdaysAtOfficeRecords()
            sb.UpdatingAttendanceYesterdaysSickLeaveRecords()
            sb.UpdatingAttendanceYesterdaysWorkFromHomeRecords()
            sb.UpdatingAttendanceYesterdaysCasualLeaveRecords()
        if CurrentDateFromAttendanceTable != todaysDate:
            sb.reset_atOffice()
            sb.reset_sickLeave()
            sb.reset_casualLeave()
            sb.reset_workFromHome()
            sb.updateAttendanceTableDate(todaysDate)
            print('Updating future leaves')
            sb.set_future_leaves_for_today()
        




@app.route('/attendanceemployees', methods=['GET'])
def attendanceemployees():
    sb = EmployeeProfileDAL()
    setAttendancetableDates()
    attendanceEmployees = sb.attendance_employees()
    employeeList = []
    for employee in attendanceEmployees:
        employeeDict = {
            "EmployeeId" : employee[0],
            "EmployeeName" : employee[1],
            "ProjectName" : employee[2],
            "AtOffice" : employee[3],
            "SickLeave" : employee[4],
            "CasualLeave" : employee[5],
            "WorkFromHome" : employee[6],
        }
        employeeList.append(employeeDict)
    return jsonify(employeeList)


@app.route('/attendanceemployeesyesterday', methods=['GET'])
def attendanceemployeesyesterday():   
    sb = EmployeeProfileDAL()
    attendanceEmployees = sb.attendance_employees_yesterday()
    employeeList = []
    for employee in attendanceEmployees:
        employeeDict = {
            "EmployeeId" : employee[0],
            "EmployeeName" : employee[1],
            "ProjectName" : employee[2],
            "AtOffice" : employee[3],
            "SickLeave" : employee[4],
            "CasualLeave" : employee[5],
            "WorkFromHome" : employee[6],
        }
        employeeList.append(employeeDict)
    return jsonify(employeeList)


@app.route('/saveattendance/<attendanceDay>', methods=['POST'])
def saveattendance(attendanceDay):
    if request.method =='POST':
        sb = EmployeeProfileDAL()
        employeeId = request.form['employeeId']
        atOffice = request.form['atOffice']
        sickLeave = request.form['sickLeave']
        casualLeave = request.form['casualLeave']
        workFromHome = request.form['workFromHome']
        leaveId = getLeaveIdFromLeaveType(sickLeave=sickLeave, casualLeave=casualLeave)
        print(f'Leave id : {leaveId}')
        attendanceDetails = AttendanceDetails(employee_id= employeeId, at_office=atOffice,sick_leave=sickLeave,casual_leave=casualLeave,work_form_home=workFromHome)
        if attendanceDay == 'today':
            sb.update_employee_attendance(attendanceDetails=attendanceDetails)
            if leaveId:                
                sb.insert_into_leave_details_table(attendanceDetails=attendanceDetails, leavetype= leaveId)
        if attendanceDay == 'yesterday':
            sb.update_employee_attendance_yesterday(attendanceDetails=attendanceDetails)
            if leaveId:
                sb.insert_into_leave_details_table_yesterday(attendanceDetails=attendanceDetails, leavetype= leaveId)
        sb.c.close()
        return "Ok"


def getLeaveIdFromLeaveType(sickLeave, casualLeave):
    leaveId = None
    if sickLeave == 'Full Day':
        leaveId = 1
    if sickLeave == 'Half Day':
        leaveId = 2
    if casualLeave == 'Full Day':
        leaveId = 4
    if casualLeave == 'Half Day':
        leaveId = 5
    return leaveId

@app.route('/downloadattendancereport', methods=['GET'])
def downloadattendancereport():
    path = "C:\\Attendance"
    try:      
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)            
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)                
    except Exception as e:
        return 'The file might be open hence failed to delete a file, Please close the file and try!'
    try:
        sb = EmployeeProfileDAL()
        #Get the count of all employees for Half Day and Full Day
        attendanceCount = sb.get_count_of_all_attendance_employees()
        attendanceCountHalfDay = sb.get_count_of_all_attendance_employees_halfDay()
        attendanceCountYesterday = sb.get_count_of_all_attendance_employees_yesterday()
        attendanceCountHalfDayYesterday = sb.get_count_of_all_attendance_employees_yesterday_halfday()

        atOfficeCountTotalToday = attendanceCount['AtOfficeCount'] + attendanceCountHalfDay['AtOfficeCountHalfday']
        sickLeaveTotalCountToday = attendanceCount['SickLeaveCount'] + attendanceCountHalfDay['SickLeaveCountHalfDay']
        casualLeaveTotalCountToday = attendanceCount['CasualLeaveCount'] + attendanceCountHalfDay['CasualLeaveCountHalfDay']
        wfhLeaveTotalCountToday = attendanceCount['WorkFromHomeCount'] + attendanceCountHalfDay['WorkFromHomeCountHalfDay']

        atOfficeCountTotalYesterday = attendanceCountYesterday['AtOfficeCount'] + attendanceCountHalfDayYesterday['AtOfficeCountHalfDay']
        wfhCountTotalYesterday = attendanceCountYesterday['WorkFromHomeCount'] + attendanceCountHalfDayYesterday['WorkFromHomeCountHalfDay']
        casualLeaveCountTotalYesterday = attendanceCountYesterday['CasualLeaveCount'] + attendanceCountHalfDayYesterday['CasualLeaveCountHalfDay']
        sickLeaveCountTotalYesterday = attendanceCountYesterday['SickLeaveCount'] + attendanceCountHalfDayYesterday['SickLeaveCountHalfDay']
        
        #Get Employee Names for all half Day and Full day
        attendanceEmployees = sb.get_all_attendance_employees()        
        attendanceEmployeesYesterday = sb.get_all_attendance_employees_yesterday()     
        attendanceEmployeesHalfDay = sb.get_all_attendance_employees_halfday()        
        attendanceEmployeesHalfDayYesterday = sb.get_all_attendance_employees_yesterday_halfday() 

        if attendanceEmployeesHalfDay["AtOfficeEmployeesHalfDay"] != 'None' and attendanceEmployees['AtOfficeEmployees'] != 'None':
            atofficeEmployeesToday = attendanceEmployeesHalfDay["AtOfficeEmployeesHalfDay"] + attendanceEmployees['AtOfficeEmployees']
        if attendanceEmployeesHalfDay["SickLeaveEmployeesHalfDay"] != 'None' and attendanceEmployees['SickLeaveEmployees'] != 'None':
            sickLeaveEmployeesToday = attendanceEmployeesHalfDay["SickLeaveEmployeesHalfDay"] + attendanceEmployees['SickLeaveEmployees']
        if attendanceEmployeesHalfDay["CasualLeaveEmployeesHalfDay"] != 'None' and attendanceEmployees['CasualLeaveEmployees'] != 'None':
            casualLeaveEmployeesToday = attendanceEmployeesHalfDay["CasualLeaveEmployeesHalfDay"] + attendanceEmployees['CasualLeaveEmployees']

        if attendanceEmployeesHalfDay["AtOfficeEmployeesHalfDay"] == 'None' and attendanceEmployees['AtOfficeEmployees'] != 'None':
            atofficeEmployeesToday = attendanceEmployees['AtOfficeEmployees']
        if attendanceEmployeesHalfDay["SickLeaveEmployeesHalfDay"] == 'None' and attendanceEmployees['SickLeaveEmployees'] != 'None':
            sickLeaveEmployeesToday = attendanceEmployees['SickLeaveEmployees']
        if attendanceEmployeesHalfDay["CasualLeaveEmployeesHalfDay"] == 'None' and attendanceEmployees['CasualLeaveEmployees'] != 'None':
            casualLeaveEmployeesToday = attendanceEmployees['CasualLeaveEmployees']

        if attendanceEmployeesHalfDay["AtOfficeEmployeesHalfDay"] != 'None' and attendanceEmployees['AtOfficeEmployees'] == 'None':
            atofficeEmployeesToday = attendanceEmployeesHalfDay["AtOfficeEmployeesHalfDay"]
        if attendanceEmployeesHalfDay["SickLeaveEmployeesHalfDay"] != 'None' and attendanceEmployees['SickLeaveEmployees'] == 'None':
            sickLeaveEmployeesToday = attendanceEmployeesHalfDay["SickLeaveEmployeesHalfDay"]
        if attendanceEmployeesHalfDay["CasualLeaveEmployeesHalfDay"] != 'None' and attendanceEmployees['CasualLeaveEmployees'] == 'None':
            casualLeaveEmployeesToday = attendanceEmployeesHalfDay["CasualLeaveEmployeesHalfDay"]

        print(f'attendanceEmployeesHalfDayYesterday :{attendanceEmployeesHalfDayYesterday}')

        if attendanceEmployeesHalfDayYesterday['AtOfficeEmployeeshalfday'] != 'None' and attendanceEmployeesYesterday['AtOfficeEmployees'] != 'None':
            atOfficeEmployeesYesterday = attendanceEmployeesHalfDayYesterday['AtOfficeEmployeeshalfday'] + attendanceEmployeesYesterday['AtOfficeEmployees']
        if attendanceEmployeesHalfDayYesterday['SickLeaveEmployeeshalfday'] != 'None'  and attendanceEmployeesYesterday['SickLeaveEmployees'] != 'None':
            sickLeaveEmployeesYesterday = attendanceEmployeesHalfDayYesterday['SickLeaveEmployeeshalfday'] + attendanceEmployeesYesterday['SickLeaveEmployees']
        if attendanceEmployeesHalfDayYesterday['CasualLeaveEmployeeshalfday'] != 'None' and attendanceEmployeesYesterday['CasualLeaveEmployees'] != 'None':
            casualLeaveEmployeesYesterday = attendanceEmployeesHalfDayYesterday['CasualLeaveEmployeeshalfday'] + attendanceEmployeesYesterday['CasualLeaveEmployees']

        if attendanceEmployeesHalfDayYesterday['AtOfficeEmployeeshalfday'] != 'None' and attendanceEmployeesYesterday['AtOfficeEmployees'] == 'None':
            atOfficeEmployeesYesterday = attendanceEmployeesHalfDayYesterday['AtOfficeEmployeeshalfday']
        if attendanceEmployeesHalfDayYesterday['SickLeaveEmployeeshalfday'] != 'None'  and attendanceEmployeesYesterday['SickLeaveEmployees'] == 'None':
            sickLeaveEmployeesYesterday = attendanceEmployeesHalfDayYesterday['SickLeaveEmployeeshalfday']
        if attendanceEmployeesHalfDayYesterday['CasualLeaveEmployeeshalfday'] != 'None' and attendanceEmployeesYesterday['CasualLeaveEmployees'] == 'None':
            casualLeaveEmployeesYesterday = attendanceEmployeesHalfDayYesterday['CasualLeaveEmployeeshalfday']

        if attendanceEmployeesHalfDayYesterday['AtOfficeEmployeeshalfday'] == 'None' and attendanceEmployeesYesterday['AtOfficeEmployees'] != 'None':
            atOfficeEmployeesYesterday = attendanceEmployeesYesterday['AtOfficeEmployees']
        if attendanceEmployeesHalfDayYesterday['SickLeaveEmployeeshalfday'] == 'None'  and attendanceEmployeesYesterday['SickLeaveEmployees'] != 'None':
            sickLeaveEmployeesYesterday = attendanceEmployeesYesterday['SickLeaveEmployees']
        if attendanceEmployeesHalfDayYesterday['CasualLeaveEmployeeshalfday'] == 'None' and attendanceEmployeesYesterday['CasualLeaveEmployees'] != 'None':
            casualLeaveEmployeesYesterday = attendanceEmployeesYesterday['CasualLeaveEmployees']

        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
            
        todaysdate = datetime.now().strftime('%d-%m-%Y')
        workbook = xlsxwriter.Workbook(f'C:\\Attendance\\Attendance_{todaysdate}.xlsx')
        worksheet = workbook.add_worksheet(todaysdate)
        #Excel Formatting
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter','border':2, 'border_color':'black'})
        bold_border_background_colour = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border':2, 'border_color':'black','bg_color': 'yellow'})
        text_wrap = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border':2, 'border_color':'black'})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter','border':2, 'border_color':'black'})

        #Setting Column Width
        worksheet.set_column("B:B",10)
        worksheet.set_column("C:C",5)
        worksheet.set_column("D:D",50)
        worksheet.set_column("E:E",15)
        worksheet.set_column("F:F",15)
        worksheet.set_column("G:G",15)
        worksheet.set_column("H:H",20)

        #Adding Data to 3rd Row
        worksheet.write('B3', 'Date', bold_border_background_colour)
        worksheet.write('C3', 'Total', bold_border_background_colour)
        worksheet.write('D3', 'At Office', bold_border_background_colour)
        worksheet.write('E3', 'Work From Home', bold_border_background_colour)
        worksheet.write('F3', 'At Customer Site', bold_border_background_colour)
        worksheet.write('G3', 'On Leave Not Sick', bold_border_background_colour)
        worksheet.write('H3', 'Sick', bold_border_background_colour)

        #adding data for yesterday
        worksheet.write('B9', 'Date', bold_border_background_colour)
        worksheet.write('C9', 'Total', bold_border_background_colour)
        worksheet.write('D9', 'At Office', bold_border_background_colour)
        worksheet.write('E9', 'Work From Home', bold_border_background_colour)
        worksheet.write('F9', 'At Customer Site', bold_border_background_colour)
        worksheet.write('G9', 'On Leave Not Sick', bold_border_background_colour)
        worksheet.write('H9', 'Sick', bold_border_background_colour)
        
        
        #Adding Data to 4th Row
        worksheet.write('B4', "", center)
        worksheet.write('C4',attendanceCount['TotalEmployeeCount'] ,center)
        worksheet.write('D4', atOfficeCountTotalToday ,center)
        worksheet.write("E4",wfhLeaveTotalCountToday,center)
        worksheet.write('F4', "", center)
        worksheet.write('G4',casualLeaveTotalCountToday,center)
        worksheet.write('H4',sickLeaveTotalCountToday,center)

        worksheet.write('B10', "", center)
        worksheet.write('C10',attendanceCountYesterday['TotalEmployeeCount'] ,center)
        worksheet.write('D10',atOfficeCountTotalYesterday ,center)
        worksheet.write("E10",wfhCountTotalYesterday ,center)
        worksheet.write('F10', "", center)
        worksheet.write('G10',casualLeaveCountTotalYesterday ,center)
        worksheet.write('H10',sickLeaveCountTotalYesterday ,center)
        
        #Adding data to 5th row
        worksheet.write('B5', todaysdate , bold)
        worksheet.write('C5', "", center)
        if attendanceEmployees['AtOfficeEmployees'] == 'None' and attendanceEmployeesHalfDay["AtOfficeEmployeesHalfDay"] == 'None':
            worksheet.write('D5',"None",text_wrap) 
        else :
            worksheet.write('D5',' , '.join(atofficeEmployeesToday),text_wrap) 

        worksheet.write('E5', "", center)
        worksheet.write('F5', "", center)
        if attendanceEmployees['CasualLeaveEmployees'] == 'None' and attendanceEmployeesHalfDay["CasualLeaveEmployeesHalfDay"] == 'None':
            worksheet.write('G5',"None",text_wrap) 
        else :
            worksheet.write('G5',' , '.join(casualLeaveEmployeesToday),text_wrap) 
            
        if attendanceEmployees['SickLeaveEmployees'] == 'None' and attendanceEmployeesHalfDay["SickLeaveEmployeesHalfDay"] == 'None':
            worksheet.write('H5',"None",text_wrap) 
        else :
            worksheet.write('H5',' , '.join(sickLeaveEmployeesToday),text_wrap) 
            

        #Adding data to 5th row
        if date.today().weekday() == 0:
            yesterday =  datetime.now() - timedelta(3)
            yesterdaysDate = (datetime.strftime(yesterday, '%d/%m/%Y'))
        else :
            yesterday =  datetime.now() - timedelta(1)
            yesterdaysDate = (datetime.strftime(yesterday, '%d/%m/%Y'))

        worksheet.write('B11', yesterdaysDate , bold)
        worksheet.write('C11', "", center)

        if attendanceEmployeesYesterday['AtOfficeEmployees'] == 'None' and attendanceEmployeesHalfDayYesterday['AtOfficeEmployeeshalfday'] == 'None':
            worksheet.write('D11',"None",text_wrap) 
        else :
            worksheet.write('D11',' , '.join(atOfficeEmployeesYesterday),text_wrap) 
        
        worksheet.write('E11', "", center)
        worksheet.write('F11', "", center)

        if attendanceEmployeesYesterday['CasualLeaveEmployees'] == 'None' and attendanceEmployeesHalfDayYesterday['CasualLeaveEmployeeshalfday'] == 'None':
            worksheet.write('G11',"None",text_wrap) 
        else :
            worksheet.write('G11',' , '.join(casualLeaveEmployeesYesterday),text_wrap)
            
        if attendanceEmployeesYesterday['SickLeaveEmployees'] == 'None' and attendanceEmployeesHalfDayYesterday['SickLeaveEmployeeshalfday'] == 'None':
            worksheet.write('H11',"None",text_wrap) 
        else :
            worksheet.write('H11',' , '.join(sickLeaveEmployeesYesterday),text_wrap) 
           
        #worksheet.write('E5',','.join(attendanceEmployees['WorkFromHomeEmployees']),text_wrap)

        workbook.close()
        
        file = f'C:\\Attendance\\Attendance_{todaysdate}.xlsx'
        return send_file(file,as_attachment= True)
    except Exception as e:
        print(f'Error when downloading report : {e}')
        return "error"       

@app.route('/projectnames', methods=['GET'])
def projectnames():
    if request.method =='GET':
        sb = EmployeeProfileDAL()
        return jsonify(sb.getProjects())



@app.route('/signout', methods=['GET'])
def signout():
    if 'user' not in session:
        app.logger.info('Logged out by user..')
        return redirect(url_for('show_login'))

    app.logger.info('Logged out by user..')
    app.logger.info('-------------------------------------------------------------------------------------')
    session.pop('user', None)
    return redirect(url_for('show_login'))

@app.route('/demo')
def dem():
    if 'user' not in session:
        return render_template("DemoCal.html")
    return redirect(url_for('show_login'))


if __name__ == '__main__':
    # initialize the log handler
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s - %(message)s")
    logHandler = RotatingFileHandler('Logs\\UserActivity.log', maxBytes=100000, backupCount=100)
    # set the log handler level
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    # set the app logger level
    app.logger.setLevel(logging.INFO)

    app.logger.addHandler(logHandler)
    app.run(host='0.0.0.0',port=80,debug=False)

    schedule.every().day.at("17:23").do(automatedExcelSheet)
    #app.run(debug=True)
    while True:
        schedule.run_pending()
        time.sleep(1)
        