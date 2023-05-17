import sqlite3
from sqlite3 import Error
import json
from flask import g
from Employee import Employee
import datetime
from datetime import timedelta,date, datetime

class EmployeeProfileDAL:
    def __init__(self):
        DATABASE = "DBN\LeaveApp.db"  # DB file initialization
        db = getattr(g, '_database', None)
        self.conn_db = sqlite3.connect(DATABASE)  # connection opening  instantiation
        print("open database successfully")
        self.c = self.conn_db.cursor()

    def read_employee(self):
        try:
            self.c.execute("select EmployeeDetails.ProjectID, EmployeeDetails.EmployeeID from EmployeeDetails")
            temp1 = self.c.fetchall()
            #print(temp1)
            print("Displaying an Employee details Table")
            self.c.execute("select EmployeeDetails.ProjectID, EmployeeDetails.EmployeeID, EmployeeMaster.EmployeeName,EmployeeDetails.EmployeeLevel,"
                           "ProjectMaster.ProjectName,ProjectMaster.Department,EmployeeDetails.Mail,EmployeeMaster.CorpID,EmployeeStatus.EmployeeWorkStatus,EmployeeDetails.Expertise "
                           "from EmployeeDetails inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus "
                           "on EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID where EmployeeStatus.EmployeeWorkStatus='Assigned'")
            rows = self.c.fetchall()
            #print("EmpId  EmpName PrismId  ProjectId")
            #for row in rows:
            #    print(row)
            return rows
        except Error as e:
            print(e)
            
    def get_project_id(self, project_name):
        try:
            self.c.execute("select ProjectID from ProjectMaster where ProjectName = '{}'".format(project_name))
            project_id = self.c.fetchall()
            return project_id[0][0]
        except Exception as e:
            print(f'Error when getting project : {e}')

            
    def attendance_employees(self):
        try:
            self.c.execute("select tbl_Attendance.EmployeeID,EmployeeMaster.EmployeeName, ProjectMaster.ProjectName, tbl_Attendance.AtOffice,tbl_Attendance.SickLeave, "
                           "tbl_Attendance.CasualLeave,tbl_Attendance.WorkFromHome from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned'")
            rows = self.c.fetchall()
            return rows
        except Error as e:
            print(e)
    
    def attendance_employees_yesterday(self):
        try:
            self.c.execute("select tbl_Attendance_Yesterday.EmployeeID,EmployeeMaster.EmployeeName, ProjectMaster.ProjectName, tbl_Attendance_Yesterday.AtOffice,tbl_Attendance_Yesterday.SickLeave, "
                           "tbl_Attendance_Yesterday.CasualLeave,tbl_Attendance_Yesterday.WorkFromHome from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned'")
            rows = self.c.fetchall()
            return rows
        except Error as e:
            print(e)


    def update_employee_attendance(self, attendanceDetails):
        try:
            print("Updating Values into tbl_Attendance ")
            
            self.c.execute("update tbl_Attendance set AtOffice = '{}' , SickLeave = '{}' , CasualLeave = '{}' , WorkFromHome = '{}'  where EmployeeId = {}".format
                           (attendanceDetails.at_office, attendanceDetails.sick_leave, attendanceDetails.casual_leave, attendanceDetails.work_form_home , int(attendanceDetails.employee_id)))
            self.conn_db.commit()
        except Error as e:
            print(e)
        
    def insert_into_leave_details_table(self, attendanceDetails, leavetype):
        try:
            self.c.execute("select CorpID from EmployeeMaster where EmployeeId = '{}'".format(int(attendanceDetails.employee_id)))
            corpid = self.c.fetchall()
            today = datetime.now()
            todaysDate = (datetime.strftime(today, '%d/%m/%Y'))  
            
            self.c.execute("select CorpID, LeaveDate from LeaveDetails where CorpID = '{}' and LeaveDate = '{}'".format(corpid[0][0] , todaysDate))  
            leaveDetails = self.c.fetchall()
            if not leaveDetails:
                self.c.execute("insert into LeaveDetails (CorpID,LeaveDate,LeaveID) values ('{}','{}','{}') ".format(corpid[0][0], todaysDate, leavetype))
                self.conn_db.commit()
            else : 
                leaveDate = leaveDetails[0][1]
                self.c.execute("update LeaveDetails set LeaveID = '{}' where CorpID = '{}' and LeaveDate = '{}'".format(leavetype , corpid[0][0], leaveDate))
                self.conn_db.commit()
        except Exception as e:
            print(f'Exception Occured : {e}')
            return e
        
    
    def update_employee_attendance_yesterday(self, attendanceDetails):
        try:
            print("Updating Values into Table")
            
            self.c.execute("update tbl_Attendance_Yesterday set AtOffice = '{}' , SickLeave = '{}' , CasualLeave = '{}' , WorkFromHome = '{}'  where EmployeeId = {}".format
                           (attendanceDetails.at_office, attendanceDetails.sick_leave, attendanceDetails.casual_leave, attendanceDetails.work_form_home , int(attendanceDetails.employee_id)))
            self.conn_db.commit()
            print("Successfully updated employee details")
        except Error as e:
            print(e)

    def insert_into_leave_details_table_yesterday(self, attendanceDetails, leavetype):
        try:
            self.c.execute("select CorpID from EmployeeMaster where EmployeeId = '{}'".format(int(attendanceDetails.employee_id)))
            corpid = self.c.fetchall()
            
            #Monday Logic
            if date.today().weekday() == 0:
                yesterday =  datetime.now() - timedelta(3)
                yesterdaysDate = (datetime.strftime(yesterday, '%d/%m/%Y'))
            else :
                yesterday =  datetime.now() - timedelta(1)
                yesterdaysDate = (datetime.strftime(yesterday, '%d/%m/%Y'))
            
            self.c.execute("select CorpID , LeaveDate, LeaveID from LeaveDetails where CorpID = '{}' and LeaveDate = '{}' ORDER BY LeaveDate DESC LIMIT 1".format(corpid[0][0],yesterdaysDate))  
            leaveDetails = self.c.fetchall()
            
            if not leaveDetails:                
                self.c.execute("insert into LeaveDetails (CorpID,LeaveDate,LeaveID) values ('{}','{}','{}') ".format(corpid[0][0], yesterdaysDate, leavetype))
                self.conn_db.commit()           
            
            if leaveDetails:
                leaveDate = leaveDetails[0][1]
                self.c.execute("update LeaveDetails set LeaveID = '{}' where CorpID = '{}' and LeaveDate = '{}'".format(leavetype , corpid[0][0], leaveDate))
                self.conn_db.commit()
            else:
                raise('No record for this corp id exists for yesterday')
        except Exception as e:
            print(f'Exception occured on adding details to attendance yesterday : {e}')
            return e

    def get_count_of_all_attendance_employees(self):
        try:
            attendanceCountDictionary = {}
            
            self.c.execute("select count(tbl_Attendance.EmployeeID) as TotalEmployeeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' and ProjectMaster.ProjectID not in ('97097','99356','99843','100852','101052','105485','106769') ")
            TotalEmployeeCount = self.c.fetchall()            
            attendanceCountDictionary["TotalEmployeeCount"] = TotalEmployeeCount[0][0]
            
            self.c.execute("select count(tbl_Attendance.EmployeeID) as AtOfficeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.AtOffice = 'Full Day' ")
            AtOfficeCount = self.c.fetchall()            
            attendanceCountDictionary["AtOfficeCount"] = AtOfficeCount[0][0]
            
            self.c.execute("select count(tbl_Attendance.EmployeeID) as SickLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.SickLeave = 'Full Day' ")
            SickLeaveCount = self.c.fetchall()
            attendanceCountDictionary["SickLeaveCount"] = SickLeaveCount[0][0]
            
            self.c.execute("select count(tbl_Attendance.EmployeeID) as CasualLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.CasualLeave = 'Full Day' ")
            CasualLeaveCount = self.c.fetchall()
            attendanceCountDictionary["CasualLeaveCount"] = CasualLeaveCount[0][0]
            
            self.c.execute("select count(tbl_Attendance.EmployeeID) as WorkFromHomeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.WorkFromHome = 'Full Day' and ProjectMaster.ProjectID not in ('97097','99356','99843','100852','101052','105485','106769')")
            WorkFromHomeCount = self.c.fetchall()
            attendanceCountDictionary["WorkFromHomeCount"] = WorkFromHomeCount[0][0]
            
            return attendanceCountDictionary
        except Exception as e:
            return e


    def get_datesCount_in_attendance_table(self):
        datesandcountdictionary = {}
        try :
            self.c.execute("SELECT count(distinct AttendanceDate) from tbl_Attendance")
            CurrentDateCountFromAttendanceTable = self.c.fetchall() 
            datesandcountdictionary["CurrentDateCountFromAttendanceTable"] = CurrentDateCountFromAttendanceTable[0][0]
            
            self.c.execute("SELECT distinct AttendanceDate from tbl_Attendance order by AttendanceDate DESC LIMIT 1")
            CurrentDateFromAttendanceTable = self.c.fetchall()
            datesandcountdictionary["CurrentDateFromAttendanceTable"] = CurrentDateFromAttendanceTable[0][0]
            
            self.c.execute("SELECT count(distinct AttendanceDate) from tbl_Attendance_Yesterday")
            YesterdaysDateCount = self.c.fetchall()
            datesandcountdictionary["YesterdaysDateCount"] = YesterdaysDateCount[0][0]
            
            self.c.execute("SELECT distinct AttendanceDate from tbl_Attendance_Yesterday order by AttendanceDate DESC LIMIT 1")
            YesterdaysDateFromTable = self.c.fetchall()
            datesandcountdictionary["YesterdaysDateFromTable"] = YesterdaysDateFromTable[0][0]
            return datesandcountdictionary
        except Exception as e :
            print('Error while fetching the dates : {e}')
            return e 
    
    def updateAttendanceTableDate(self, attendanceTableDate):
        try:
            print("Updating the date in Attendance table")            
            self.c.execute("update tbl_Attendance set AttendanceDate = '{}'".format(attendanceTableDate))
            self.conn_db.commit()
            print("Updated the date to todays date")
        except Error as e:
            print(e)
            
    def updateAttendanceYesterdayTableDate(self, attendanceYesterdayTableDate):
        try:
            print("Updating the date in AttendanceYesterday table")            
            self.c.execute("update tbl_Attendance_Yesterday set AttendanceDate = '{}'".format(attendanceYesterdayTableDate))
            self.conn_db.commit()
            print("Updated the date to yesterdays date")
        except Error as e:
            print(e)
    
    def UpdatingAttendanceYesterdaysAtOfficeRecords(self):
        try:
            print('Updating At Office Records')
            self.c.execute("update tbl_Attendance_Yesterday set AtOffice = (select AtOffice from tbl_Attendance where tbl_Attendance.EmployeeId = tbl_Attendance_Yesterday.EmployeeId)")
            self.conn_db.commit()
            print("Records Cleared")
        except Error as e:
            print(e)
    
    def UpdatingAttendanceYesterdaysSickLeaveRecords(self):
        try:
            print('Updating Sick Leave records')
            self.c.execute("update tbl_Attendance_Yesterday set SickLeave = (select SickLeave from tbl_Attendance where tbl_Attendance.EmployeeId = tbl_Attendance_Yesterday.EmployeeId)")
            self.conn_db.commit()
            print("Records Cleared")
        except Error as e:
            print(e)
    
    def UpdatingAttendanceYesterdaysCasualLeaveRecords(self):
        try:
            print('Updating Casual Leave records')
            self.c.execute("update tbl_Attendance_Yesterday set CasualLeave = (select CasualLeave from tbl_Attendance where tbl_Attendance.EmployeeId = tbl_Attendance_Yesterday.EmployeeId)")
            self.conn_db.commit()
            print("Records Cleared")
        except Error as e:
            print(e)
    
    def UpdatingAttendanceYesterdaysWorkFromHomeRecords(self):
        try:
            print('Updating Casual Leave records')
            self.c.execute("update tbl_Attendance_Yesterday set WorkFromHome = (select WorkFromHome from tbl_Attendance where tbl_Attendance.EmployeeId = tbl_Attendance_Yesterday.EmployeeId)")
            self.conn_db.commit()
            print("Records Cleared")
        except Error as e:
            print(e)
    
    def get_all_attendance_employees(self):
        try:
            attendanceEmployeesDictionary = {}
            
            self.c.execute("select tbl_Attendance.Employeename as AtOfficeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.AtOffice = 'Full Day' ")
            AtOfficeEmployees = [item[0] for item in  self.c.fetchall()]           
            if len(AtOfficeEmployees) == 0:
                attendanceEmployeesDictionary["AtOfficeEmployees"] = "None"
            else :
                attendanceEmployeesDictionary["AtOfficeEmployees"] = AtOfficeEmployees
            
            self.c.execute("select tbl_Attendance.Employeename as SickLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.SickLeave = 'Full Day' ")
            SickLeaveEmployees = [item[0] for item in  self.c.fetchall()]
            if len(SickLeaveEmployees) == 0:
                attendanceEmployeesDictionary["SickLeaveEmployees"] = "None"
            else :
                attendanceEmployeesDictionary["SickLeaveEmployees"] = SickLeaveEmployees
            
            self.c.execute("select tbl_Attendance.Employeename as CasualLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.CasualLeave = 'Full Day' ")
            CasualLeaveEmployees = [item[0] for item in  self.c.fetchall()]
            if len(CasualLeaveEmployees) == 0:
                attendanceEmployeesDictionary["CasualLeaveEmployees"] = "None"
            else :
                attendanceEmployeesDictionary["CasualLeaveEmployees"] = CasualLeaveEmployees
            
            self.c.execute("select tbl_Attendance.Employeename as WorkFromHomeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.WorkFromHome = 'Full Day' ")
            WorkFromHomeEmployees = [item[0] for item in  self.c.fetchall()]
            if len(WorkFromHomeEmployees) == 0:
                attendanceEmployeesDictionary["WorkFromHomeEmployees"] = "None"
            else :
                attendanceEmployeesDictionary["WorkFromHomeEmployees"] = WorkFromHomeEmployees
            
            return attendanceEmployeesDictionary
        except Exception as e:
            return e

    def delete_employee(self, employeeId):
        try:
            print(f"Deleting an Employee details from a Table with id : {employeeId}")
            self.c.execute("update EmployeeStatus set EmployeeWorkStatus = 'UnAssigned' where EmployeeId = {}".format
                           (int(employeeId)))
            # self.c.execute("update tbl_Attendance set EmployeeStatus = 'UnAssigned' where EmployeeId = {}".format
            #                (int(employeeId)))
            # self.c.execute("update tbl_Attendance_Yesterday set EmployeeStatus = 'UnAssigned' where EmployeeId = {}".format
            #                (int(employeeId)))
            self.conn_db.commit()
            print("Successfully updated employee details")
            return 'employee deleted'
        except Error as e:
            print(e)

    def getProjects(self):
        self.c.execute("select ProjectName from ProjectMaster")
        projects = self.c.fetchall()
        return projects

    def read_employee_in_dict(self):
        try:
            self.c.execute("select EmployeeDetails.ProjectID, EmployeeDetails.EmployeeID, EmployeeMaster.EmployeeName,"
                           "ProjectMaster.ProjectName,ProjectMaster.Department,EmployeeDetails.Mail,EmployeeMaster.CorpID "
                           "from EmployeeDetails inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus "
                           "on EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID where EmployeeStatus.EmployeeWorkStatus='Assigned'")
            entries=[dict(ProjectID=row[0], EmployeeID=row[1], EmployeeName=row[2], ProjectName= row[3], Department=row[4], Mail=row[5], CorpID=row[6]) for row in self.c.fetchall()]
            #print(entries)
            return entries
        except Error as e:
            print(e)

    def add_employee(self, employee):
        try:
            print(f"Adding Details to table : {employee.employee_id}")
            sql = "insert into EmployeeMaster(CorpID,EmployeeName,EmployeeID) values('{}','{}','{}')".format(employee.corp_idM.lower(), employee.employee_name, employee.employee_id)
            self.c.execute(sql)
            self.c.execute("insert into EmployeeStatus(EmployeeWorkStatus,EmployeeID) values('Assigned','{}')".format(employee.employee_id))
            self.c.execute("SELECT MAX(EmployeeDetailsID) FROM EmployeeDetails")
            NextEmployeeDetailsID=self.c.fetchone()[0]+1
            self.c.execute("insert into EmployeeDetails(EmployeeDetailsID,EmployeeID,ProjectID,CorpID,Mail,Expertise,EmployeeLevel)"
                           "values('{}','{}','{}','{}','{}','{}','{}')".format (NextEmployeeDetailsID, employee.employee_id, employee.project_id, employee.corp_idM.lower(), employee.email,employee.expertise, employee.employeeLevel))
            today = datetime.now()
            todaysDate = (datetime.strftime(today, '%d/%m/%Y'))
            insertIntoAttendance = "INSERT into tbl_Attendance (EmployeeId, EmployeeName , AtOffice, SickLeave, CasualLeave, WorkFromHome, AttendanceDate) VALUES ('{}', '{}', 'No','No', 'No', 'Full Day','{}')".format(employee.employee_id, employee.employee_name, todaysDate)
            self.c.execute(insertIntoAttendance)
            
            yesterday =  datetime.now() - timedelta(1)
            yesterdaysDate = (datetime.strftime(yesterday, '%d/%m/%Y'))
            insertIntoAttendanceYesterday = "INSERT into tbl_Attendance_Yesterday (EmployeeId, EmployeeName , AtOffice, SickLeave, CasualLeave, WorkFromHome, AttendanceDate) VALUES ('{}', '{}', 'No','No', 'No', 'Full Day','{}')".format(employee.employee_id, employee.employee_name, yesterdaysDate)
            self.c.execute(insertIntoAttendanceYesterday)       
            
            self.conn_db.commit()
        except Error as e:
            print("Error Info", e)


    def get_current_employee_Info(self, corpId):
        try:
            print("Displaying an Employee details Table")
            command_text = "Select EmployeeMaster.EmployeeName,EmployeeDetails.Mail,EmployeeMaster.EmployeeID," \
            "EmployeeDetails.ManagerID from EmployeeMaster inner join EmployeeDetails on EmployeeMaster.CorpID = EmployeeDetails.CorpID " \
            "where EmployeeDetails.CorpID='{}'".format(corpId.lower())
            self.c.execute(command_text)
            rows = self.c.fetchall()
            #print("EmpId  EmpName PrismId  ProjectId")
            #for row in rows:
            #    print(row)
            return rows
        except Error as e:
            print(e)

    

    def update_employee(self, employee):
        try:
            print("Updating Values into Table")
            self.c.execute('update EmployeeMaster set EmployeeName = "{}" where EmployeeId = {}'.format
                           (employee.employee_name, int(employee.employee_id)))

            self.c.execute('update EmployeeDetails set ProjectID = {} , Expertise = "{}", EmployeeLevel = "{}" where EmployeeId = {}'.format
                           (int(employee.project_id), employee.expertise, employee.employeeLevel, int(employee.employee_id)))

            self.c.execute("update EmployeeStatus set EmployeeWorkStatus = '{}'  where EmployeeId = {}".format(employee.employeeODCStatus,int(employee.employee_id)))
            self.conn_db.commit()
            print("Successfully updated employee details")
        except Error as e:
            print(e)

    def update_status(self,employeeId):
        try:
            print("Updating Status into Table")
            self.c.execute("update EmployeeStatus set EmployeeWorkStatus = '{}'  where EmployeeId = {}"
                           .format("Unassigned",int((employeeId)[0])))
            self.conn_db.commit()
            print("Successfully updated employee details")
        except Error as e:
            print(e)

    def readTotalLeavesForAnEmployee(self,corpid):
        try:
            self.c.execute("Select LeaveDetails.LeaveDate, LeaveMaster.LeaveID from "
                           "LeaveDetails inner join LeaveMaster on "
                           "LeaveDetails.LeaveID=LeaveMaster.LeaveID "
                           "where CorpID='{}'".format(corpid))
            rows = self.c.fetchall()
            #for row in rows:
            #    print(row)
            return rows
        except Error as e:
            print(e)

    # for export current month details
    # def read_leaves_corpid(self, corp_id, month, year):
    #     try:
    #         # and LeaveDate LIKE '%/{}/{}'
    #         desired = "/" + str(month) + "/" + str(year)
    #         sql=("Select * from EmployeeLeaveInfo where CorpId=? and LeaveDate LIKE '%"+ desired +"'")
    #         self.c.execute(sql, (corp_id,))
    #         rows = self.c.fetchall()
    #         for row in rows:
    #          print(row)
    #         return rows
    #     except Error as e:
    #         print(e)

    def read_leaves_type(self, corp_id, month, year):
        try:
            # and LeaveDate LIKE '%/{}/{}'
            desired = "/" + str(month) + "/" + str(year)
            sql=("Select LeaveDetails.LeaveDate, LeaveDetails.LeaveID from LeaveDetails "
                 "where CorpID = ? and LeaveDate LIKE '%"+ desired +"'")
            # sql=("Select LeaveDetails.LeaveID from LeaveDetails where CorpId = '{}' and LeaveDate LIKE '%{}'".format(corp_id,desired))
            self.c.execute(sql, (corp_id,))
            rows = self.c.fetchall()
            #for row in rows:
            # print(row)
            return rows
        except Error as e:
            print(e)

    # def read_leaves_report(self, requiredMonth,requiredYear):
    #     try:
    #         # and LeaveDate LIKE '%/{}/{}'
    #         desired="/"+str(requiredMonth)+"/"+str(requiredYear)
    #         print(desired)
    #         self.c.execute("Select * from EmployeeLeaveInfo where LeaveDate LIKE '%"+ desired +"'")
    #         rows = self.c.fetchall()
    #         for row in rows:
    #          print(row)
    #         return rows
    #     except Error as e:
    #         print(e)

    def submit_leaves(self, employeeLeave,corpId,leavetype):
        try:
            print("Feeding to database for leaves")
            self.c.execute("insert into LeaveDetails (CorpID,LeaveDate,LeaveID) "
                           "values ('{}','{}','{}') ".format(corpId, employeeLeave, leavetype, corpId))
            self.conn_db.commit()
            print("Successfully updated employee details")
        except Error as e:
            print(e)

    # def cancel_leaves(self, employeeLeave,employeeId):
    #     try:
    #         print("Deleting from database for leaves")
    #         self.c.execute("delete from EmployeeLeaveInfo where LeaveDate = ? and Employee_Id = ? ", (employeeLeave,employeeId))
    #         self.conn_db.commit()
    #         print("Successfully updated employee details")
    #     except Error as e:
    #         print(e)

    #for server side validation in form filling
    def gettingEmployeeDetailsForRepeatedEntries(self, formElement):
        try:
             print("getting the EmpId from db")
             # print(formElement["EmployeeID"])
             print(formElement.keys())

             for keyFromDict in formElement:
                 key = keyFromDict
                 #print(key)
             if key == "EmployeeID":
                 self.c.execute("select {} from EmployeeMaster where EmployeeID = {}".format(key,int(formElement[key])))
             elif(key == "Mail"):
                 self.c.execute("select {} from EmployeeDetails where upper({}) = upper('{}')".format(key, key, formElement[key]))
             else:
                 self.c.execute("select {} from EmployeeMaster where upper({}) = upper('{}')".format(key,key, formElement[key]))
             returnedColoumn = self.c.fetchall()
             ret_value = 0
             if len(returnedColoumn) != 0:
                  # if str(returnedColoumn[0][0]) == formElement[key]:
                ret_value = 1
             return ret_value
        except Error as e:
              print(e)

    def gettingAssignedEmployeeToManager(self, manager_id):
        try:
            self.c.execute("select EmployeeMaster.EmployeeID,EmployeeMaster.EmployeeName,EmployeeDetails.Mail,ProjectMaster.ProjectName, EmployeeMaster.CorpID "
                           "from EmployeeDetails inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus "
                           "on EmployeeDetails.EmployeeID = EmployeeMaster.EmployeeID "
                           "and EmployeeDetails.ProjectID = ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeDetails.EmployeeID "
                           "where ManagerID = {}   and EmployeeStatus.EmployeeWorkStatus='Assigned'".format(manager_id))
            entries=[dict(EmployeeID=row[0], EmployeeName=row[1], ProjectName= row[2], Mail=row[3], CorpID=row[4]) for row in self.c.fetchall()]
            self.conn_db.commit()
            return entries
        except Error as e:
            print(e)

    def AssiningToManager(self,manager_id,employee_list):
        try:
            for el in employee_list:
                self.c.execute("update EmployeeDetails set ManagerID = {} where EmployeeDetails.EmployeeID = {}".format(manager_id, int(el)))
            self.conn_db.commit()
            return "AssinedToManager"
        except Error as e:
            print(e)

    def gettingRespectiveManagerEmail(self, corp_id):
        try:
            self.c.execute(" select EmployeeDetails.Mail from EmployeeDetails "
                           "where EmployeeDetails.EmployeeID="
                           "(select EmployeeDetails.ManagerID from EmployeeDetails "
                           "where EmployeeDetails.CorpID='{}')".format(corp_id))
            ManagersMail =self.c.fetchall()
            self.conn_db.commit()
            return ManagersMail
        except Error as e:
            print(e)

    def add_lab_request(self, description,Employee_name,project_name, today, id):
        try:
            print("Feeding to database for Lab Requests")
            sql = "insert into Labrequests (RequestId,Project,Employeename,Description, RequestData, Active) values ('{}', '{}','{}','{}', '{}', '1') ".format(id, project_name, Employee_name, description, today)
            self.c.execute(sql)
            self.conn_db.commit()
            print("Successfully updated lab request details")
        except Error as e:
            print(e)

    def delete_lab_request(self, id):
        try:
            print("De-activate to database for Lab Requests")
            self.c.execute("update  Labrequests  set Active = 0 where RequestId = '{}' ".format(id))
            self.conn_db.commit()
            print("Successfully updated lab request details")
        except Error as e:
            print(e)

    def read_lab_requests(self):
        try:
            # and LeaveDate LIKE '%/{}/{}'
            sql=("Select RequestId, Employeename, Project, Description, RequestData from Labrequests where Active= 1")
            # sql=("Select LeaveDetails.LeaveID from LeaveDetails where CorpId = '{}' and LeaveDate LIKE '%{}'".format(corp_id,desired))
            self.c.execute(sql)
            rows = self.c.fetchall()
            #for row in rows:
             #print(row)
            return rows
        except Error as e:
            print(e)
    # def compare_employee_name(self, emp_name):
    #     try:
    #          print("getting the EmpId from db")
    #          self.c.execute("Select EmployeeName from EmployeeMaster where EmployeeName = ?", [emp_name])
    #          empname = self.c.fetchall()
    #          ret_value = 0
    #          if len(empname) != 0:
    #             if str(empname[0][0]) == emp_name:
    #                 ret_value = 1
    #          return ret_value
    #     except Error as e:
    #          print(e)
        # return render_template("/LeaveApp.html", **locals())
    def get_count_of_all_attendance_employees_yesterday(self):
            try:
                attendanceCountDictionary = {}
                
                self.c.execute("select count(tbl_Attendance_Yesterday.EmployeeID) as TotalEmployeeCount from EmployeeDetails "
                               "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                               "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                               "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                               "where EmployeeStatus.EmployeeWorkStatus='Assigned' and ProjectMaster.ProjectID not in ('97097','99356','99843','100852','101052','105485','106769') ")
                TotalEmployeeCount = self.c.fetchall()            
                attendanceCountDictionary["TotalEmployeeCount"] = TotalEmployeeCount[0][0]
                
                self.c.execute("select count(tbl_Attendance_Yesterday.EmployeeID) as AtOfficeCount from EmployeeDetails "
                               "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                               "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                               "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                               "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.AtOffice = 'Full Day' ")
                AtOfficeCount = self.c.fetchall()            
                attendanceCountDictionary["AtOfficeCount"] = AtOfficeCount[0][0]
                
                self.c.execute("select count(tbl_Attendance_Yesterday.EmployeeID) as SickLeaveCount from EmployeeDetails "
                               "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                               "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                               "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                               "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.SickLeave = 'Full Day' ")
                SickLeaveCount = self.c.fetchall()
                attendanceCountDictionary["SickLeaveCount"] = SickLeaveCount[0][0]
                
                self.c.execute("select count(tbl_Attendance_Yesterday.EmployeeID) as CasualLeaveCount from EmployeeDetails "
                               "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                               "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                               "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                               "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.CasualLeave = 'Full Day' ")
                CasualLeaveCount = self.c.fetchall()
                attendanceCountDictionary["CasualLeaveCount"] = CasualLeaveCount[0][0]
                
                self.c.execute("select count(tbl_Attendance_Yesterday.EmployeeID) as WorkFromHomeCount from EmployeeDetails "
                               "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                               "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                               "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                               "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.WorkFromHome = 'Full Day' and ProjectMaster.ProjectID not in ('97097','99356','99843','100852','101052','105485','106769') ")
                WorkFromHomeCount = self.c.fetchall()
                attendanceCountDictionary["WorkFromHomeCount"] = WorkFromHomeCount[0][0]
                
                return attendanceCountDictionary
            except Exception as e:
                return e
    
    
    def get_all_attendance_employees_yesterday(self):
            try:
                attendanceEmployeesDictionary = {}
                
                self.c.execute("select tbl_Attendance_Yesterday.Employeename as AtOfficeCount from EmployeeDetails "
                               "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                               "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                               "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                               "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.AtOffice = 'Full Day' ")
                AtOfficeEmployees = [item[0] for item in  self.c.fetchall()]           
                if len(AtOfficeEmployees) == 0:
                    attendanceEmployeesDictionary["AtOfficeEmployees"] = "None"
                else :
                    attendanceEmployeesDictionary["AtOfficeEmployees"] = AtOfficeEmployees
                
                self.c.execute("select tbl_Attendance_Yesterday.Employeename as SickLeaveCount from EmployeeDetails "
                               "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                               "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                               "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                               "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.SickLeave = 'Full Day' ")
                SickLeaveEmployees = [item[0] for item in  self.c.fetchall()]
                if len(SickLeaveEmployees) == 0:
                    attendanceEmployeesDictionary["SickLeaveEmployees"] = "None"
                else :
                    attendanceEmployeesDictionary["SickLeaveEmployees"] = SickLeaveEmployees
                
                self.c.execute("select tbl_Attendance_Yesterday.Employeename as CasualLeaveCount from EmployeeDetails "
                               "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                               "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                               "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                               "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.CasualLeave = 'Full Day' ")
                CasualLeaveEmployees = [item[0] for item in  self.c.fetchall()]
                if len(CasualLeaveEmployees) == 0:
                    attendanceEmployeesDictionary["CasualLeaveEmployees"] = "None"
                else :
                    attendanceEmployeesDictionary["CasualLeaveEmployees"] = CasualLeaveEmployees
                
                self.c.execute("select tbl_Attendance_Yesterday.Employeename as WorkFromHomeCount from EmployeeDetails "
                               "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                               "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                               "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                               "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.WorkFromHome = 'Full Day' ")
                WorkFromHomeEmployees = [item[0] for item in  self.c.fetchall()]
                if len(WorkFromHomeEmployees) == 0:
                    attendanceEmployeesDictionary["WorkFromHomeEmployees"] = "None"
                else :
                    attendanceEmployeesDictionary["WorkFromHomeEmployees"] = WorkFromHomeEmployees
                
                return attendanceEmployeesDictionary
            except Exception as e:
                return e
    

    def get_count_of_all_attendance_employees_halfDay(self):
        try:
            attendanceCountDictionaryHalfaDay = {}
            
            self.c.execute("select count(tbl_Attendance.EmployeeID) as AtOfficeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.AtOffice = 'Half Day' ")
            AtOfficeCountHalfDay = self.c.fetchall()            
            attendanceCountDictionaryHalfaDay["AtOfficeCountHalfday"] = AtOfficeCountHalfDay[0][0]
            
            self.c.execute("select count(tbl_Attendance.EmployeeID) as SickLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.SickLeave = 'Half Day' ")
            SickLeaveCountHalfDay = self.c.fetchall()
            attendanceCountDictionaryHalfaDay["SickLeaveCountHalfDay"] = SickLeaveCountHalfDay[0][0]
            
            self.c.execute("select count(tbl_Attendance.EmployeeID) as CasualLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.CasualLeave = 'Half Day' ")
            CasualLeaveCountHalfDay = self.c.fetchall()
            attendanceCountDictionaryHalfaDay["CasualLeaveCountHalfDay"] = CasualLeaveCountHalfDay[0][0]
            
            self.c.execute("select count(tbl_Attendance.EmployeeID) as WorkFromHomeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.WorkFromHome = 'Half Day' ")
            WorkFromHomeCountHalfDay = self.c.fetchall()
            attendanceCountDictionaryHalfaDay["WorkFromHomeCountHalfDay"] = WorkFromHomeCountHalfDay[0][0]
            
            return attendanceCountDictionaryHalfaDay
        except Exception as e:
            return e

    def get_all_attendance_employees_halfday(self):
        try:
            attendanceEmployeesDictionaryHalfDay = {}
            
            self.c.execute("select tbl_Attendance.Employeename as AtOfficeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.AtOffice = 'Half Day' ")
            AtOfficeEmployeesHalfDay = [item[0] for item in  self.c.fetchall()]          
            if len(AtOfficeEmployeesHalfDay) == 0:
                attendanceEmployeesDictionaryHalfDay["AtOfficeEmployeesHalfDay"] = "None"
            else :
                AtOfficeEmployeesHalfDayNew = [x + '(0.5)' for x in AtOfficeEmployeesHalfDay]
                attendanceEmployeesDictionaryHalfDay["AtOfficeEmployeesHalfDay"] = AtOfficeEmployeesHalfDayNew
            
            self.c.execute("select tbl_Attendance.Employeename as SickLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.SickLeave = 'Half Day' ")
            SickLeaveEmployeesHalfDay = [item[0] for item in  self.c.fetchall()]
            if len(SickLeaveEmployeesHalfDay) == 0:
                attendanceEmployeesDictionaryHalfDay["SickLeaveEmployeesHalfDay"] = "None"
            else :
                SickLeaveEmployeesHalfDayNew = [x + '(0.5)' for x in SickLeaveEmployeesHalfDay]
                attendanceEmployeesDictionaryHalfDay["SickLeaveEmployeesHalfDay"] = SickLeaveEmployeesHalfDayNew
            
            self.c.execute("select tbl_Attendance.Employeename as CasualLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.CasualLeave = 'Half Day' ")
            CasualLeaveEmployeesHalfDay = [item[0] for item in  self.c.fetchall()]
            if len(CasualLeaveEmployeesHalfDay) == 0:
                attendanceEmployeesDictionaryHalfDay["CasualLeaveEmployeesHalfDay"] = "None"
            else :
                CasualLeaveEmployeesHalfDayNew = [x + '(0.5)' for x in CasualLeaveEmployeesHalfDay]
                attendanceEmployeesDictionaryHalfDay["CasualLeaveEmployeesHalfDay"] = CasualLeaveEmployeesHalfDayNew
            
            self.c.execute("select tbl_Attendance.Employeename as WorkFromHomeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance.WorkFromHome = 'Half Day' ")
            WorkFromHomeEmployeesHalfDay = [item[0] for item in  self.c.fetchall()]
            if len(WorkFromHomeEmployeesHalfDay) == 0:
                attendanceEmployeesDictionaryHalfDay["WorkFromHomeEmployeesHalfDay"] = "None"
            else :
                WorkFromHomeEmployeesHalfDayNew = [x + '(0.5)' for x in WorkFromHomeEmployeesHalfDay]
                attendanceEmployeesDictionaryHalfDay["WorkFromHomeEmployeesHalfDay"] = WorkFromHomeEmployeesHalfDayNew
            
            return attendanceEmployeesDictionaryHalfDay
        except Exception as e:
            return e


    def get_count_of_all_attendance_employees_yesterday_halfday(self):
        try:
            attendanceCountDictionaryHalfDay = {}
            
            self.c.execute("select count(tbl_Attendance_Yesterday.EmployeeID) as AtOfficeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.AtOffice = 'Half Day' ")
            AtOfficeCountHalfDay = self.c.fetchall()            
            attendanceCountDictionaryHalfDay["AtOfficeCountHalfDay"] = AtOfficeCountHalfDay[0][0]
            
            self.c.execute("select count(tbl_Attendance_Yesterday.EmployeeID) as SickLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.SickLeave = 'Half Day' ")
            SickLeaveCountHalfDay = self.c.fetchall()
            attendanceCountDictionaryHalfDay["SickLeaveCountHalfDay"] = SickLeaveCountHalfDay[0][0]
            
            self.c.execute("select count(tbl_Attendance_Yesterday.EmployeeID) as CasualLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.CasualLeave = 'Half Day' ")
            CasualLeaveCountHalfDay = self.c.fetchall()
            attendanceCountDictionaryHalfDay["CasualLeaveCountHalfDay"] = CasualLeaveCountHalfDay[0][0]
            
            self.c.execute("select count(tbl_Attendance_Yesterday.EmployeeID) as WorkFromHomeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.WorkFromHome = 'Half Day' ")
            WorkFromHomeCountHalfDay = self.c.fetchall()
            attendanceCountDictionaryHalfDay["WorkFromHomeCountHalfDay"] = WorkFromHomeCountHalfDay[0][0]
            
            return attendanceCountDictionaryHalfDay
        except Exception as e:
            return e

    def get_all_attendance_employees_yesterday_halfday(self):
        try:
            attendanceEmployeesDictionaryhalfday = {}
            
            self.c.execute("select tbl_Attendance_Yesterday.Employeename as AtOfficeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.AtOffice = 'Half Day' ")
            AtOfficeEmployeeshalfday = [item[0] for item in  self.c.fetchall()]           
            if len(AtOfficeEmployeeshalfday) == 0:
                attendanceEmployeesDictionaryhalfday["AtOfficeEmployeeshalfday"] = "None"
            else :
                AtOfficeEmployeesHalfDayNew = [x + '(0.5)' for x in AtOfficeEmployeeshalfday]
                attendanceEmployeesDictionaryhalfday["AtOfficeEmployeeshalfday"] = AtOfficeEmployeesHalfDayNew
            
            self.c.execute("select tbl_Attendance_Yesterday.Employeename as SickLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.SickLeave = 'Half Day' ")
            SickLeaveEmployeeshalfday = [item[0] for item in  self.c.fetchall()]
            if len(SickLeaveEmployeeshalfday) == 0:
                attendanceEmployeesDictionaryhalfday["SickLeaveEmployeeshalfday"] = "None"
            else :
                SickLeaveEmployeesHalfDayNew = [x + '(0.5)' for x in SickLeaveEmployeeshalfday]
                attendanceEmployeesDictionaryhalfday["SickLeaveEmployeeshalfday"] = SickLeaveEmployeesHalfDayNew
            
            self.c.execute("select tbl_Attendance_Yesterday.Employeename as CasualLeaveCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.CasualLeave = 'Half Day' ")
            CasualLeaveEmployeeshalfday = [item[0] for item in  self.c.fetchall()]
            if len(CasualLeaveEmployeeshalfday) == 0:
                attendanceEmployeesDictionaryhalfday["CasualLeaveEmployeeshalfday"] = "None"
            else :
                CasualLeaveEmployeesHalfDayNew = [x + '(0.5)' for x in CasualLeaveEmployeeshalfday]
                attendanceEmployeesDictionaryhalfday["CasualLeaveEmployeeshalfday"] = CasualLeaveEmployeesHalfDayNew
            
            self.c.execute("select tbl_Attendance_Yesterday.Employeename as WorkFromHomeCount from EmployeeDetails "
                           "inner join EmployeeMaster inner join ProjectMaster inner join EmployeeStatus inner join tbl_Attendance_Yesterday on "
                           "EmployeeDetails.CorpID=EmployeeMaster.CorpID and EmployeeDetails.ProjectID=ProjectMaster.ProjectID "
                           "and EmployeeStatus.EmployeeID=EmployeeMaster.EmployeeID and EmployeeMaster.EmployeeID=tbl_Attendance_Yesterday.EmployeeID "
                           "where EmployeeStatus.EmployeeWorkStatus='Assigned' AND tbl_Attendance_Yesterday.WorkFromHome = 'Half Day' ")
            WorkFromHomeEmployeeshalfday = [item[0] for item in  self.c.fetchall()]
            if len(WorkFromHomeEmployeeshalfday) == 0:
                attendanceEmployeesDictionaryhalfday["WorkFromHomeEmployeeshalfday"] = "None"
            else :
                WorkFromHomeEmployeesHalfDayNew = [x + '(0.5)' for x in WorkFromHomeEmployeeshalfday]
                attendanceEmployeesDictionaryhalfday["WorkFromHomeEmployeeshalfday"] = WorkFromHomeEmployeesHalfDayNew
            
            return attendanceEmployeesDictionaryhalfday
        except Exception as e:
            return e

    def get_attendance_date_from_db(self):
        self.c.execute("select DISTINCT(AttendanceDate) from tbl_Attendance")
        attendanceDate = self.c.fetchall()
        return attendanceDate[0][0]
    
    def reset_atOffice(self):
        try:
            self.c.execute("update tbl_Attendance set AtOffice = 'No' WHERE AtOffice = 'Full Day' or AtOffice = 'Half Day'")
            self.conn_db.commit()
        except Exception as e:
            print(f'Error Occured when resetting at office')
            return e

    def reset_sickLeave(self):
        try:
            self.c.execute("update tbl_Attendance set SickLeave = 'No' WHERE SickLeave = 'Full Day' or SickLeave = 'Half Day'")
            self.conn_db.commit()
        except Exception as e:
            print(f'Error Occured when resetting sick leave')
            return e

    def reset_casualLeave(self):
        try:
            self.c.execute("update tbl_Attendance set CasualLeave = 'No' WHERE CasualLeave = 'Full Day' or CasualLeave = 'Half Day'")
            self.conn_db.commit()
        except Exception as e:
            print(f'Error Occured when resetting casual leave')
            return e

    def reset_workFromHome(self):
        try:
            self.c.execute("update tbl_Attendance set WorkFromHome = 'Full Day' WHERE WorkFromHome = 'No' or WorkFromHome = 'Half Day'")
            self.conn_db.commit()
        except Exception as e:
            print(f'Error Occured when resetting workfromhome')
            return e

    def set_future_leaves_for_today(self):
        try:            
            today = datetime.now()
            todaysDate = (datetime.strftime(today, '%d/%m/%Y'))
            self.c.execute("select CorpID, LeaveID from LeaveDetails where LeaveDate = '{}'".format(todaysDate))
            results = self.c.fetchall()
            for item in results:
                self.c.execute("SELECT EmployeeId from EmployeeMaster where CorpID = '{}'".format(item[0].lower()))
                leaveEmployees = self.c.fetchall()
                for employee in leaveEmployees:
                    if item[1] == '1':
                        self.c.execute("update tbl_Attendance set SickLeave = 'Full Day', WorkFromHome = 'No' WHERE EmployeeId = '{}'".format(employee[0]))
                        self.conn_db.commit()
                    if item[1] == '4':
                        self.c.execute("update tbl_Attendance set CasualLeave = 'Full Day', WorkFromHome = 'No' WHERE EmployeeId = '{}'".format(employee[0]))
                        self.conn_db.commit()
        except Exception as e:
            print(e)
            return e