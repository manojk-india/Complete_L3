import pandas as pd
import random
from random import randint
from datetime import datetime, timedelta

#Define 6 sprints with 2 weeks duration
sprint_data={
    "Sprint 1": {"state":"Completed", "start_date": datetime(2025,1,1), "end_date": datetime(2025,1,13),"status":["Done"]},
    "Sprint 2": {"state":"Completed", "start_date": datetime(2025,1,14), "end_date": datetime(2025,1,27),"status":["Done"]},
    "Sprint 3": {"state":"Completed", "start_date": datetime(2025,1,28), "end_date": datetime(2025,2,10),"status":["Done"]},
    "Sprint 4": {"state":"Completed", "start_date": datetime(2025,2,11), "end_date": datetime(2025,2,24),"status":["Done"]},

    "Sprint 5": {"state":"Completed", "start_date": datetime(2025,2,25), "end_date": datetime(2025,3,11),"status":["Done"]},
    "Sprint 6": {"state":"Completed", "start_date": datetime(2025,3,12), "end_date": datetime(2025,3,25),"status":["Done"]},
    "Sprint 7": {"state":"Completed", "start_date": datetime(2025,3,26), "end_date": datetime(2025,4,8),"status":["Done"]},	
    "Sprint 8": {"state":"Active", "start_date": datetime(2025,4,9), "end_date": datetime(2025,4,22),"status":["In Progress","Done","To Do"]},	
    "Sprint 9": {"state":"Future", "start_date": datetime(2025,4,23), "end_date": datetime(2025,5,6),"status":["To Do"]},		
    "Sprint 10": {"state":"Future", "start_date": datetime(2025,5,7), "end_date": datetime(2025,5,20),"status":["To Do"]},	

}


boards=["CDF","EBSNF","TES1","TES2","APS1","APS2"]
employement_type={
    "Alice": "FTC",
    "Bob": "FTC",
    "Rishika": "FTE",
    "Hari": "FTE",
    "Apoorva": "FTE",
    "David":"FTC",
    "Pavithra": "FTE",	
    "Alok": "FTE",
    "Peter": "FTC",
    "Sai":"FTE",
    "Krithika":"FTE",
    "Seetha":"FTC",
    "Rasheed":"FTE",
    "Rachin":"FTC",
    "Nitish":"FTE",
    "Noor":"FTE",
    "Khaleel":"FTC",
    "Vikram":"FTC",
    "Dube":"FTE",
    "Ashwin":"FTC",
}

assignees={
    "CDF": ["Alice","Bob","Rishika","Hari","Apoorva"],
    "EBSNF": ["Apoorva","David","Pavithra","Alok","Peter"],
    "TES1": ["Sai","Krithika","David"],
    "TES2": ["Seetha","Rasheed","Rachin"],	
    "APS1": ["Nitish","Noor","Khaleel"],
    "APS2": ["Vikram","Dube","Ashwin"],
}

reporters={
    "CDF":["Tony","Naruto"],
    "EBSNF":["Zoro","Hinata"],
    "TES1":["Shubman","Ishan"],
    "TES2":["Smrithi","Pradeep"],
    "APS1":["Shreya","Madhu"],
    "APS2":["Bhuvi","Ravi"],	
}

priorities=["Low","Medium","High","Critical"]
issue_types=["Defect","Story","Task"]

CDF={"DIS-1":"RTB","DIS-2":"CTB","DIS-3":"RTB","DIS-4":"CTB"}
EBSNF={"DIS-5":"RTB","DIS-6":"CTB","DIS-7":"RTB"}	
TES1={"TES-1":"CTB","TES-2":"RTB"}
TES2={"TES-3":"RTB","TES-4":"CTB"}
APS1={"APS-1":"CTB","APS-2":"RTB"}	
APS2={"APS-3":"RTB","APS-4":"CTB"}

CDF_fix_versions=["CDF1-8783","CDF1-8784","CDF1-8785","CDF1-8786"]
EBSNF_fix_versions=["EBSNF1-8783","EBSNF1-8784","EBSNF1-8785","EBSNF1-8786"]
TES1_fix_versions=["TES1-8783","TES1-8784","TES1-8785","TES1-8786"]
TES2_fix_versions=["TES2-8783","TES2-8784","TES2-8785","TES2-8786"]
APS1_fix_versions=["APS1-8783","APS1-8784","APS1-8785","APS1-8786"]
APS2_fix_versions=["APS2-8783","APS2-8784","APS2-8785","APS2-8786"]


Epic_issue_counts={
    "DIS-1": 1,"DIS-2": 1,"DIS-3": 1,"DIS-4": 1,"DIS-5": 1,"DIS-6": 1,"DIS-7": 1,
    "TES-1": 1,"TES-2": 1,"TES-3": 1,"TES-4": 1,
    "APS-1": 1,"APS-2": 1,"APS-3": 1,"APS-4": 1,
}

data=[]
for i in range(1,401):
    board=random.choice(boards)
    sprint_name=random.choice(list(sprint_data.keys()))
    sprint_details=sprint_data[sprint_name]
    sprint_start=sprint_details["start_date"]
    sprint_end=sprint_details["end_date"]
    sprint_state=sprint_details["state"]

    if(board=="CDF"):
        epic_id=random.choice(list(CDF.keys()))
        requested_by=CDF[epic_id]
        fix=random.choice(CDF_fix_versions)
    elif(board=="EBSNF"):
        epic_id=random.choice(list(EBSNF.keys()))
        requested_by=EBSNF[epic_id]
        fix=random.choice(EBSNF_fix_versions)
    elif(board=="TES1"):
        epic_id=random.choice(list(TES1.keys()))
        requested_by=TES1[epic_id]
        fix=random.choice(TES1_fix_versions)
    elif(board=="TES2"):
        epic_id=random.choice(list(TES2.keys()))
        requested_by=TES2[epic_id]
        fix=random.choice(TES2_fix_versions)
    elif(board=="APS1"):
        epic_id=random.choice(list(APS1.keys()))
        requested_by=APS1[epic_id]
        fix=random.choice(APS1_fix_versions)
    else:
        epic_id=random.choice(list(APS2.keys()))
        requested_by=APS2[epic_id]
        fix=random.choice(APS2_fix_versions)
    

    issue_type=random.choice(issue_types)
    priority=random.choice(priorities)

    assignee=random.choice(assignees[board])
    role=employement_type[assignee]
    reporter=random.choice(reporters[board])

    status=random.choice(sprint_details["status"])
    story_points=random.choice([1,2,3,5,])

    issue_key=epic_id+"-"+str(Epic_issue_counts[epic_id])
    Epic_issue_counts[epic_id]+=1

    priority=random.choice(priorities)
    closed=None

    if(status in ["To Do","In Progress"]):
        closed=None
    else:
        if(sprint_state=="Completed"):
            closed=(sprint_end-timedelta(days=randint(1,13))).strftime("%Y-%m-%d")
        else:
            delta=datetime.today()-sprint_start
            closed=(sprint_start+timedelta(days=delta.days)).strftime("%Y-%m-%d")

    data.append({
        "key":issue_key,
        "board":board,
        "summary":f"TASK {i} for {board}",
        "description":f"Description for Task {i} in {board}",
        "acceptance_criteria":f"Acceptance criteria for issue type {issue_type} in {board} with issue key {issue_key}",
        "status": status,
        "assignee":assignee,
        "reporter":reporter,
        "priority":priority,
        "issue_type": issue_type,
        "created":(datetime.today()-timedelta(days=random.randint(5,30))).strftime("%Y-%m-%d"),
         "closed": closed,
         "labels":random.choice([["backend"],["frontend"],["bugfix"],["enhancement"],["UI"],[]]),
         "components":random.choice([["Auth Service"],["Payment Service"],["UI"],["API"],["Database"],[]]),
         "sprint":sprint_name,
         "sprint_state":sprint_state,
         "sprint_start_date":sprint_start.strftime("%Y-%m-%d"),
         "sprint_end_date":sprint_end.strftime("%Y-%m-%d"),
         "story_points":story_points,
         "epic_id":epic_id,
         "employee_type":role,
         "requested_by":requested_by,
         "fix_versions":fix
    })

for i in range(1,11):
    board="CDF"
    fix_versions=random.choice(CDF_fix_versions)
    epic_id=random.choice(list(CDF.keys()))
    requested_by=CDF[epic_id]
    story_points=random.choice([1,2,3,5,8])
    issue_key=epic_id+"-"+str(Epic_issue_counts[epic_id])
    Epic_issue_counts[epic_id]+=1

    sprint_name=None
    sprint_state=None
    sprint_start=None
    sprint_end=None

    priority=random.choice(priorities)
    assignee=random.choice(assignees[board])
    role=employement_type[assignee]
    reporter=random.choice(reporters[board])

    issue_type=random.choice(issue_types)
    data.append({
        "key":issue_key,
        "board":board,
        "summary":f"Backlog {i} for {board}",
        "description":f"Description for unassigned backlog {i} in {board}",
        "acceptance_criteria":f"Acceptance criteria for issue type {issue_type} in {board} with issue key {issue_key}",
        "status": "To Do",
        "assignee":assignee,
        "reporter":reporter,
        "priority":priority,
        "issue_type": issue_type,
        "created":(datetime.today()-timedelta(days=random.randint(5,30))).strftime("%Y-%m-%d"),
         "closed": None,
         "labels":random.choice([["backend"],["frontend"],["bugfix"],["enhancement"],["UI"],[]]),
         "components":random.choice([["Auth Service"],["Payment Service"],["UI"],["API"],["Database"],[]]),
         "sprint":sprint_name,
         "sprint_state":sprint_state,
         "sprint_start_date":sprint_start,
         "sprint_end_date":sprint_end,
         "story_points":story_points,
         "epic_id":epic_id,
         "employee_type":role,
         "requested_by":requested_by,
         "fix_versions":fix_versions	
    })

for i in range(1,11):
    board="EBSNF"
    fix_versions=random.choice(EBSNF_fix_versions)
    epic_id=random.choice(list(EBSNF.keys()))
    requested_by=EBSNF[epic_id]
    story_points=random.choice([1,2,3,5,8])
    issue_key=epic_id+"-"+str(Epic_issue_counts[epic_id])
    Epic_issue_counts[epic_id]+=1
    
    sprint_start=None
    sprint_end=None
    sprint_name=None
    sprint_state=None
    priority=random.choice(priorities)
    assignee=random.choice(assignees[board])
    role=employement_type[assignee]
    reporter=random.choice(reporters[board])
    issue_type=random.choice(issue_types)
    data.append({
        "key":issue_key,
        "board":board,
        "summary":f"Backlog {i} for {board}",
        "description":f"Description for unassigned backlog {i} in {board}",
        "acceptance_criteria":f"Acceptance criteria for issue type {issue_type} in {board} with issue key {issue_key}",
        "status": "To Do",
        "assignee":assignee,
        "reporter":reporter,
        "priority":priority,
        "issue_type": issue_type,
        "created":(datetime.today()-timedelta(days=random.randint(5,30))).strftime("%Y-%m-%d"),
         "closed": None,
         "labels":random.choice([["backend"],["frontend"],["bugfix"],["enhancement"],["UI"],[]]),
         "components":random.choice([["Auth Service"],["Payment Service"],["UI"],["API"],["Database"],[]]),
         "sprint":sprint_name,
         "sprint_state":sprint_state,
         "sprint_start_date":sprint_start,
         "sprint_end_date":sprint_end,
         "story_points":story_points,
         "epic_id":epic_id,
         "employee_type":role,
         "requested_by":requested_by,
         "fix_versions":fix_versions
    })

for i in range(1,11):
    board="TES1"
    fix_versions=random.choice(TES1_fix_versions)
    epic_id=random.choice(list(TES1.keys()))
    requested_by=TES1[epic_id]
    story_points=random.choice([1,2,3,5,8])
    issue_key=epic_id+"-"+str(Epic_issue_counts[epic_id])
    Epic_issue_counts[epic_id]+=1
    
    sprint_start=None
    sprint_end=None
    sprint_name=None
    sprint_state=None
    priority=random.choice(priorities)
    assignee=random.choice(assignees[board])
    role=employement_type[assignee]
    reporter=random.choice(reporters[board])
    issue_type=random.choice(issue_types)
    data.append({
        "key":issue_key,
        "board":board,
        "summary":f"Backlog {i} for {board}",
        "description":f"Description for unassigned backlog {i} in {board}",
        "acceptance_criteria":f"Acceptance criteria for issue type {issue_type} in {board} with issue key {issue_key}",
        "status": "To Do",
        "assignee":assignee,
        "reporter":reporter,
        "priority":priority,
        "issue_type": issue_type,
        "created":(datetime.today()-timedelta(days=random.randint(5,30))).strftime("%Y-%m-%d"),
         "closed": None,
         "labels":random.choice([["backend"],["frontend"],["bugfix"],["enhancement"],["UI"],[]]),
         "components":random.choice([["Auth Service"],["Payment Service"],["UI"],["API"],["Database"],[]]),
         "sprint":sprint_name,
         "sprint_state":sprint_state,
         "sprint_start_date":sprint_start,
         "sprint_end_date":sprint_end,
         "story_points":story_points,
         "epic_id":epic_id,
         "employee_type":role,
         "requested_by":requested_by,
         "fix_versions":fix_versions
    })

for i in range(1,11):

    board="TES2"
    fix_versions=random.choice(TES2_fix_versions)
    epic_id=random.choice(list(TES2.keys()))
    requested_by=TES2[epic_id]
    story_points=random.choice([1,2,3,5,8])
    issue_key=epic_id+"-"+str(Epic_issue_counts[epic_id])
    Epic_issue_counts[epic_id]+=1
    
    sprint_start=None
    sprint_end=None
    sprint_name=None
    sprint_state=None
    priority=random.choice(priorities)
    assignee=random.choice(assignees[board])
    role=employement_type[assignee]
    reporter=random.choice(reporters[board])
    issue_type=random.choice(issue_types)
    data.append({
        "key":issue_key,
        "board":board,
        "summary":f"Backlog {i} for {board}",
        "description":f"Description for unassigned backlog {i} in {board}",
        "acceptance_criteria":f"Acceptance criteria for issue type {issue_type} in {board} with issue key {issue_key}",
        "status": "To Do",
        "assignee":assignee,
        "reporter":reporter,
        "priority":priority,
        "issue_type": issue_type,
        "created":(datetime.today()-timedelta(days=random.randint(5,30))).strftime("%Y-%m-%d"),
         "closed": None,
         "labels":random.choice([["backend"],["frontend"],["bugfix"],["enhancement"],["UI"],[]]),
         "components":random.choice([["Auth Service"],["Payment Service"],["UI"],["API"],["Database"],[]]),
         "sprint":sprint_name,
         "sprint_state":sprint_state,
         "sprint_start_date":sprint_start,
         "sprint_end_date":sprint_end,
         "story_points":story_points,
         "epic_id":epic_id,
         "employee_type":role,
         "requested_by":requested_by,
         "fix_versions":fix_versions
    })
for i in range(1,11):   
    board="APS1"
    fix_versions=random.choice(APS1_fix_versions)
    epic_id=random.choice(list(APS1.keys()))
    requested_by=APS1[epic_id]
    story_points=random.choice([1,2,3,5,8])
    issue_key=epic_id+"-"+str(Epic_issue_counts[epic_id])
    Epic_issue_counts[epic_id]+=1
    sprint_start=None
    sprint_end=None
    sprint_name=None
    priority=random.choice(priorities)
    assignee=random.choice(assignees[board])
    role=employement_type[assignee]
    reporter=random.choice(reporters[board])
    issue_type=random.choice(issue_types)
    data.append({
        "key":issue_key,
        "board":board,
        "summary":f"Backlog {i} for {board}",
        "description":f"Description for unassigned backlog {i} in {board}",
        "acceptance_criteria":f"Acceptance criteria for issue type {issue_type} in {board} with issue key {issue_key}",
        "status": "To Do",
        "assignee":assignee,
        "reporter":reporter,
        "priority":priority,
        "issue_type": issue_type,
        "created":(datetime.today()-timedelta(days=random.randint(5,30))).strftime("%Y-%m-%d"),
         "closed": None,
         "labels":random.choice([["backend"],["frontend"],["bugfix"],["enhancement"],["UI"],[]]),
         "components":random.choice([["Auth Service"],["Payment Service"],["UI"],["API"],["Database"],[]]),
         "sprint":sprint_name,
         "sprint_state":sprint_state,
         "sprint_start_date":sprint_start,
         "sprint_end_date":sprint_end,
         "story_points":story_points,
         "epic_id":epic_id,
         "employee_type":role,
         "requested_by":requested_by,
         "fix_versions":fix_versions
    })
for i in range(1,11):
    board="APS2"
    fix_versions=random.choice(APS2_fix_versions)
    epic_id=random.choice(list(APS2.keys()))
    requested_by=APS2[epic_id]
    story_points=random.choice([1,2,3,5,8])
    issue_key=epic_id+"-"+str(Epic_issue_counts[epic_id])
    Epic_issue_counts[epic_id]+=1
    
    sprint_start=None
    sprint_end=None
    sprint_name=None
    priority=random.choice(priorities)
    assignee=random.choice(assignees[board])
    role=employement_type[assignee]
    reporter=random.choice(reporters[board])
    issue_type=random.choice(issue_types)
    data.append({
        "key":issue_key,
        "board":board,
        "summary":f"Backlog {i} for {board}",
        "description":f"Description for unassigned backlog {i} in {board}",
        "acceptance_criteria":f"Acceptance criteria for issue type {issue_type} in {board} with issue key {issue_key}",
        "status": "To Do",
        "assignee":assignee,
        "reporter":reporter,
        "priority":priority,
        "issue_type": issue_type,
        "created":(datetime.today()-timedelta(days=random.randint(5,30))).strftime("%Y-%m-%d"),
         "closed": None,
         "labels":random.choice([["backend"],["frontend"],["bugfix"],["enhancement"],["UI"],[]]),
         "components":random.choice([["Auth Service"],["Payment Service"],["UI"],["API"],["Database"],[]]),
         "sprint":sprint_name,
         "sprint_state":sprint_state,
         "sprint_start_date":sprint_start,
         "sprint_end_date":sprint_end,
         "story_points":story_points,
         "epic_id":epic_id,
         "employee_type":role,
         "requested_by":requested_by,
         "fix_versions":fix_versions
    })


df=pd.DataFrame(data)
df.to_csv("generated_files/new_custom.csv",index=False)