class Employee:
    def __init__(self, employee_id, employee_name, project_id, project_name, corp_idM, email, department, employeeODCStatus,expertise,employeeLevel):
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.project_id = project_id
        self.project_name = project_name
        self.corp_idM = corp_idM
        self.email = email
        self.department = department
        self.employeeODCStatus = employeeODCStatus
        self.expertise=expertise
        self.employeeLevel = employeeLevel



class LeaveDetails:
    def __init__(self, employee_name, employee_id, LeaveOn, Managername):
        self.employee_name = employee_name
        self.employee_id = employee_id
        self.LeaveOn = LeaveOn
        self.Managername = Managername

class AttendanceDetails:
    def __init__(self, employee_id, at_office, sick_leave, casual_leave, work_form_home):
        self.employee_id = employee_id
        self.at_office = at_office
        self.sick_leave = sick_leave
        self.casual_leave = casual_leave
        self.work_form_home = work_form_home