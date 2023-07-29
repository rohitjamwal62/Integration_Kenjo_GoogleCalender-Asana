import requests,json
from datetime import datetime, timedelta

API_KEY = "616737154909e74397c66cadf5d25b69863d458a557a0640"
url = f"https://api.kenjo.io/api/v1/auth/login"
Calender_Id = "deepak@ellstudio.com"
Client_Id = "321584590268-gnkbefhdi97pgdjlnpbogc7.apps.googleusercontent.com"
Client_Secret = "GOCSPX-jf1dXyaoXFOrX4EPB44oNF3x"
Refresh_Token = "1//04q1htytMDXjrCgYIARAIrzNsBiSngBEFrJ75AvNZ-vqDBWvwfqRe5mrGOkyndCT9pfFvkeWNH4Jme9t_7JEMtKA"

Assignee_Id = "98415183688592"
Workspace_Id = "98415208778478"
Project_Id = "1204938336442838"
Asana_Token = "Bearer 1/1204884847377343:af582a40cd30a0ff7920e56a07c0eace"

current_date = datetime.now().strftime("%Y-%m-%d") #Get Only Date
# Current Time Format
current_datetime = datetime.now()
Current_Time = str(current_datetime).split(' ')[1].split('.')[0]

# Add 90 days to the current date
new_date = str(current_datetime + timedelta(days=90)).split(' ')[0]

# Kenjo Create Token
payload = json.dumps({"apiKey": API_KEY})
Kenjo_Token_headers = {'Origin': 'https://api.kenjo.io','Content-Type': 'application/json'}
response = requests.request("POST", url, headers=Kenjo_Token_headers, data=payload)
if response.status_code == 200:
    Token = json.loads(response.text).get('token')

# Minues Date from current date
time_difference = timedelta(hours=5, minutes=30)
result_datetime = current_datetime - time_difference
Kenjo_Current_Time = str(result_datetime).split(' ')[1].split('.')[0]
Kenjo_Current_Date = str(result_datetime).split(' ')[0]

# Original Date time
# Kenjo_Current_Time = Current_Time
# Kenjo_Current_Date = current_date
# Calender Token
url = "https://oauth2.googleapis.com/token"
payload = f'client_id={Client_Id}&client_secret={Client_Secret}&refresh_token={Refresh_Token}&grant_type=refresh_token'
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
response = requests.request("POST", url, headers=headers, data=payload)
if response.status_code == 200:
    Calender_Token = json.loads(response.text).get('access_token')
Calender_Headers = {'Authorization': f'Bearer {Calender_Token}','Accept': 'application/json','Content-Type': 'application/json'}



# Kenjo Get Time Off API 
From = current_date
To = new_date
url = f"https://api.kenjo.io/api/v1/time-off/requests?from={From}&to={To}"
Kenjo_headers = {'Authorization': f'{Token}','Origin': 'https://api.kenjo.io'}
response = requests.request("GET", url, headers=Kenjo_headers)
if response.status_code == 200:
    records = json.loads(response.text).get('data')
    for rec in records:
        Kenjo_Time = str(rec.get('_createdAt')).split('T')[1].split('.')[0] # Kenjo Time Format
        # print(Kenjo_Time,"===========================================",Kenjo_Current_Time)
        Kenjo_Date_Here = str(rec.get('_createdAt')).split('T')[0]
        Description = rec.get('description')
        if Kenjo_Date_Here == Kenjo_Current_Date:
            # print(Kenjo_Time,"===========================================",Kenjo_Current_Time)
            # Filter Hour, Minutes and Seconds of Current and Kenjo Time
            Cur_Hour =  Kenjo_Current_Time.split(':')[0]
            Cur_Min = Kenjo_Current_Time.split(':')[1]
            Kejo_Hour = Kenjo_Time.split(':')[0]
            Kenjo_Min = Kenjo_Time.split(':')[1]
            Store_Cur_Hour = str(int(Cur_Hour) - 1)
            
            if len(Store_Cur_Hour) == 1: 
                Store_Current_Hour = "0" + Store_Cur_Hour
            else:
                Store_Current_Hour = Store_Cur_Hour
            # print("Kenjo hour:",Kejo_Hour,"Store Current Hours:",Store_Current_Hour,"Current hour:",Cur_Hour,"Kenjo hour:",Kejo_Hour)
            if Cur_Hour == Kejo_Hour or Kejo_Hour == Store_Current_Hour and int(Cur_Min) <= int(Kenjo_Min):
                # print(Kenjo_Time,"===========================================",Kenjo_Current_Time)
                if Description == '':
                    Description = "Not Available"
                else:
                    Description = Description 
                
                
                # Get And Match Event
                url = "https://www.googleapis.com/calendar/v3/calendars/deepak@ellerystudio.com/events"
                response = requests.request("GET", url, headers=Calender_Headers)
                if response.status_code == 200:
                    Get_Calender_Records = json.loads(response.text)
                    Collect_Summary = [rec.get('summary') for rec in Get_Calender_Records.get('items')]
                    if Description not in Collect_Summary:
                        pass

                # Create Event
                if rec.get('status') == 'Approved' or rec.get('status') == 'Processed':
                    print("Status is Aproved____")
                    url = f"https://www.googleapis.com/calendar/v3/calendars/{Calender_Id}/events"
                    payload = json.dumps({
                        "summary": Description,
                        "start": {"dateTime": rec.get('from'),"timeZone": "America/New_York"},
                        "end": {"dateTime": rec.get('to'),"timeZone": "America/New_York"},
    
                        "eventType": "outOfOffice",
                        "transparency": "transparent",
                        "visibility": "private"
    
                    })
  
                    response = requests.request("POST", url, headers=Calender_Headers, data=payload)
                    if response.status_code == 200 :
                        print("Records is created on Google Calender-----------------",response.status_code)
                        calender_Records = json.loads(response.text)
                        # print(calender_Records)

                    # Get Tasana Tasks And Match
                    url = f"https://app.asana.com/api/1.0/tasks?workspace={Workspace_Id}&projects{Project_Id}=&assignee={Assignee_Id}"
                    Asana_Headers = {'Authorization': Asana_Token,'Content-Type': 'application/json'}
                    response = requests.request("GET", url, headers=Asana_Headers)
                    if response.status_code == 200:
                        Asana_Records = json.loads(response.text).get('data')
                        Asana_Name_Collect = [rec.get('name') for rec in Asana_Records]
                        if Description not in Asana_Name_Collect: #Check existing
                            # Create Task On Asana
                            print("Creating Records into the Asana")
                            url = "https://app.asana.com/api/1.0/tasks"
                            payload = json.dumps({
                            "data": {
                                    "workspace": Workspace_Id,
                                    "name": Description,
                                    "notes": "This is a sample task created via Kenjo",
                                    "assignee": Assignee_Id,
                                    "projects": [Project_Id],
                                    "start_on":str(rec.get('from')),
                                    "due_on":str(rec.get('to')) 
                            }
                            })
                            response = requests.request("POST", url, headers=Asana_Headers, data=payload)
                            print("Task is created on Asana----------",response.status_code)
                            output = {"response":response.text}
                            
                if rec.get('status') == 'Submitted':
                    pass