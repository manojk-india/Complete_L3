# Here is where our helper function will be present of all kind ....
import csv
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer, util
from datetime import datetime, timedelta
import requests
import json
import os
from requests.auth import HTTPBasicAuth
from crewai import Process, Agent, Task, Crew, LLM
import pandas as pd
from datetime import datetime

def find_present_words_case_insensitive(query):
    # Convert query to lower case for case-insensitive comparison
    query_lower = query.lower()

    word_list=["cdf","ebsnf","tes1","tes2","dis1","dis2"]
    # Collect words that are present in the query (case-insensitive)
    found = [word for word in word_list if word.lower() in query_lower]
    if found:
        return found[0]
    else:
        return None
    
# writing it into checkpoint file for better debugging 
def write_to_checkpoint_file(data, file_path='checkpoint.txt'):
    with open(file_path, 'a') as file:
        file.write(data + '\n')

# function that returns the L1 board id for the given board name -- to be done 
def get_board_id(board_name):
    board_ids = {
        "cdf": 39,
        "ebsnf": 38,
        "tes1": 42,
        "tes2": 43,
        "aps1": 40,
        "aps2": 41
    }
    return board_ids.get(board_name.lower(), None)  # Return None if not found



def embed_query(user_query):
    # This function will take the query and embed it using the LLM model
    # For now, we will just return the query as is
    queries = [
        "Story points assigned to person x in y board in sprint n",
        "RTB/CTB utilization of y board in sprint n",
        "RTB/CTB utilization of y person in sprint n",
        "FTE/FTC utilization of y board in sprint n",
        "Backlog health for y board",
        "JIRA hygiene for x board"
    ]
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    query_embeddings = model.encode(queries, convert_to_tensor=True)
    input_embedding = model.encode(user_query, convert_to_tensor=True)
    scores = util.cos_sim(input_embedding, query_embeddings)
    best_match_idx = scores.argmax()
    return queries[best_match_idx], scores[0][best_match_idx].item(), best_match_idx

    
# getting current sprint name
def get_current_sprint():
    # Sprint 1 starts on Jan 1, 2025
    sprint_start = datetime.strptime("2025-01-01", "%Y-%m-%d")
    sprint_duration = timedelta(weeks=2)
    sprints = []
    current = sprint_start

    # Generate sprint ranges for the whole year
    while current.year == 2025:
        sprint_end = current + sprint_duration - timedelta(days=1)
        sprints.append((current, sprint_end))
        current += sprint_duration

    today = datetime.now()
    for i, (start, end) in enumerate(sprints, start=1):
        if start <= today <= end:
            return f"sprint {i}"
    return None  # If today is not in any sprint (e.g., outside 2025)

# function that returns the sprint id 
def get_sprint_id(board_name, sprint_name):
    sprint_ids = {
        "cdf": {
            "sprint 1": 64,
            "sprint 2": 65,
            "sprint 3": 66,
            "sprint 4": 67,
            "sprint 5": 68,
            "sprint 6": 69,
            "sprint 7": 70,
            "sprint 8": 71,
            "sprint 9": 72,
            "sprint 10": 73,
            "sprint 11": 166,
        },
        "ebsnf": {
            "sprint 1": 54,
            "sprint 2": 55,
            "sprint 3": 56,
            "sprint 4": 57,
            "sprint 5": 58,
            "sprint 6": 59,
            "sprint 7": 60,
            "sprint 8": 61,
            "sprint 9": 62,
            "sprint 10": 63,
            "sprint 11": 167,
        },
        "aps1": {
            "sprint 1": 74,
            "sprint 2": 78,
            "sprint 3": 79,
            "sprint 4": 80,
            "sprint 5": 81,
            "sprint 6": 82,
            "sprint 7": 83,
            "sprint 8": 84,
            "sprint 9": 85,
            "sprint 10": 86,
            "sprint 11": 170,
        },
        "tes1": {
            "sprint 1": 76,
            "sprint 2": 96,
            "sprint 3": 97,
            "sprint 4": 98,
            "sprint 5": 99,
            "sprint 6": 100,
            "sprint 7": 101,
            "sprint 8": 102,
            "sprint 9": 103,
            "sprint 10": 104,
            "sprint 11": 168,

        },
        
        "aps2": {
            "sprint 1": 75,
            "sprint 2": 87,
            "sprint 3": 88,
            "sprint 4": 89,
            "sprint 5": 90,
            "sprint 6": 91,
            "sprint 7": 92,
            "sprint 8": 93,
            "sprint 9": 94,
            "sprint 10": 95,
            "sprint 11": 171,
        }  # Add other boards and their sprints here
    }
   
    return sprint_ids.get(board_name.lower(), {}).get(sprint_name.lower(), None)  


def get_sprint_name(board_name, sprint_id):
    """
    Returns the sprint name for a given board name and sprint ID.
    """
    sprint_ids = {
        "cdf": {
            "Sprint 1": 64,
            "Sprint 2": 65,
            "Sprint 3": 66,
            "Sprint 4": 67,
            "Sprint 5": 68,
            "Sprint 6": 69,
            "Sprint 7": 70,
            "Sprint 8": 71,
            "Sprint 9": 72,
            "Sprint 10": 73,
            "Sprint 11": 166,
        },
        "ebsnf": {
            "Sprint 1": 54,
            "Sprint 2": 55,
            "Sprint 3": 56,
            "Sprint 4": 57,
            "Sprint 5": 58,
            "Sprint 6": 59,
            "Sprint 7": 60,
            "Sprint 8": 61,
            "Sprint 9": 62,
            "Sprint 10": 63,
            "Sprint 11": 167,
        },
        "aps1": {
            "Sprint 1": 74,
            "Sprint 2": 78,
            "Sprint 3": 79,
            "Sprint 4": 80,
            "Sprint 5": 81,
            "Sprint 6": 82,
            "Sprint 7": 83,
            "Sprint 8": 84,
            "Sprint 9": 85,
            "Sprint 10": 86,
            "Sprint 11": 170,
        },
        "tes1": {
            "Sprint 1": 76,
            "Sprint 2": 96,
            "Sprint 3": 97,
            "Sprint 4": 98,
            "Sprint 5": 99,
            "Sprint 6": 100,
            "Sprint 7": 101,
            "Sprint 8": 102,
            "Sprint 9": 103,
            "Sprint 10": 104,
            "Sprint 11": 168,
        },
        "aps2": {
            "Sprint 1": 75,
            "Sprint 2": 87,
            "Sprint 3": 88,
            "Sprint 4": 89,
            "Sprint 5": 90,
            "Sprint 6": 91,
            "Sprint 7": 92,
            "Sprint 8": 93,
            "Sprint 9": 94,
            "Sprint 10": 95,
            "Sprint 11": 171,
        }
    }

    # Reverse the mapping to find sprint name by sprint ID
    board_sprints = sprint_ids.get(board_name.lower(), {})
    for sprint_name, id in board_sprints.items():
        if id == sprint_id:
            return sprint_name
    return None  # Return None if sprint ID is not found


# api caller helper function for tool calling
def api_helper(sprint_id: int, jql:str, output_file: str) -> None:
    url = f"https://wellsfargo-jira-test.atlassian.net/rest/agile/1.0/sprint/{sprint_id}/issue"
    
    # Authentication
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')
    
    # Request parameters
    params = {
        'startAt': 0,
        'maxResults': 1000
    }
    if jql:
        params['jql'] = jql
    
    headers = {'Accept': 'application/json'}
    auth = HTTPBasicAuth(email, api_token)
    
    try:
        # First read existing data if file exists
        existing_issues = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, 'r') as f:
                try:
                    existing_issues = json.load(f)
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse existing JSON in {output_file}")
                    existing_issues = []

        # Fetch new data
        new_issues = []
        while True:
            response = requests.get(url, headers=headers, auth=auth, params=params)
            response.raise_for_status()
            
            data = response.json()
            new_issues.extend(data['issues'])
            
            if data['startAt'] + data['maxResults'] >= data['total']:
                break
                
            params['startAt'] += data['maxResults']

        # Combine existing and new issues
        all_issues = existing_issues + new_issues

        # Save combined data back to file
        with open(output_file, 'w') as f:  # Note: using 'w' instead of 'a'
            json.dump(all_issues, f, indent=2)  # Note: fixed typo 'dmp' to 'dump'

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")


# getting previous sprint ids for the given board name and current sprint id -- mock function for now ..need to feed in data
def get_previous_sprint_ids(board_name, current_sprint_id):
    dictionary = {
        "cdf": [64,65,66,67,68,69,70,71,72,73,166],
        "aps1": [74,78,79,80,81,82,83,84,85,86,170],
        "aps2": [74,87,88,89,90,91,92,93,94,95,171],	
        "ebsnf": [54,55,56,57,58,59,60,61,62,63,167],
        "tes1": [76,96,97,98,99,100,101,102,103,104,168],

        # Add other boards here
    }
    idx=dictionary.get(board_name.lower()).index(current_sprint_id)
    if idx == 0:
        return []
    elif idx < 6:
        return dictionary.get(board_name.lower())[:idx]
    else:
        return dictionary.get(board_name.lower())[idx-6:idx]
    
# getting future 2 sprints 
def get_future_sprint_ids(board_name, current_sprint_id):
    dictionary = {
        "cdf": [64,65,66,67,68,69,70,71,72,73,166],
        "aps1": [74,78,79,80,81,82,83,84,85,86,170],
        "aps2": [74,87,88,89,90,91,92,93,94,95,171],	
        "ebsnf": [54,55,56,57,58,59,60,61,62,63,167],
        "tes1": [76,96,97,98,99,100,101,102,103,104,168],

        # Add other boards here
    }
    idx=dictionary.get(board_name.lower()).index(current_sprint_id)
    return [dictionary.get(board_name.lower())[idx+1],dictionary.get(board_name.lower())[idx+2]]
    

# coversting json to csv
def json_to_csv(json_file,csv_file) -> None:
    """
    Convert Jira features JSON to CSV with specified fields
    
    Args:
        json_file: Path to input JSON file
        csv_file: Path to output CSV file
    """

    # Define CSV field headers
    field_names = [
        "key",
        "issue_type",
        "parent_key",
        "project_key",
        "fix_versions",
        "status",
        "sprint",
        "sprint_status",
        "priority",
        "labels",
        "assignee",
        "components",
        "description",
        "summary",
        "acceptance_crieteria",
        "reporter",	
        "story_points",
        
    ]

    # Read JSON data
    with open(json_file, 'r',encoding='utf-8') as f:
        data = json.load(f)
    
    # Prepare CSV rows
    rows = []
    for issue in data:
        row = {
            "key": issue.get("key"),
            "issue_type": issue.get("fields", {}).get("issuetype", {}).get("name"),
            "parent_key": issue.get("fields", {}).get("parent", {}).get("key"),
            "project_key": issue.get("fields", {}).get("project", {}).get("key"),
            "fix_versions": ", ".join([version["name"] for version in issue.get("fields", {}).get("fixVersions", [])]),
            "status": issue.get("fields", {}).get("status", {}).get("name"),
            "sprint": ", ".join([sprint["name"] for sprint in issue.get("fields", {}).get("customfield_10020", [])]),
            "sprint_status": ", ".join([sprint["state"] for sprint in issue.get("fields", {}).get("customfield_10020", [])]),
            "priority": issue.get("fields", {}).get("priority", {}).get("name"),
            "labels": ", ".join(issue.get("fields", {}).get("labels", [])),
            "assignee": issue.get("fields").get("assignee", {}).get("displayName", "") if issue.get("fields").get("assignee") else "",
            "components": ", ".join([component["name"] for component in issue.get("fields", {}).get("components", [])]),
            "description": issue.get("fields", {}).get("description"),
            "summary": issue.get("fields", {}).get("summary"),
            "acceptance_crieteria": issue.get("fields", {}).get('customfield_10042'),
            "reporter": issue.get('fields',{}).get('reporter',{}).get('displayName'),
            "story_points": issue.get('fields',{}).get('customfield_10039')
        }
        rows.append(row)

    # Write to CSV
    with open(csv_file, 'w', newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)

# embedded function for L1 query classifier
def embed_query(user_query):
    # This function will take the query and embed it using the LLM model
    # For now, we will just return the query as is
    queries = [
        "Story points assigned to person x in y board in sprint n",
        "RTB/CTB utilization of y board in sprint n",
        "RTB/CTB utilization of y person in sprint n",
        "FTE/FTC utilization of y board in sprint n",
        "Backlog health for y board",
        "JIRA hygiene for x board"
    ]
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    query_embeddings = model.encode(queries, convert_to_tensor=True)
    input_embedding = model.encode(user_query, convert_to_tensor=True)
    scores = util.cos_sim(input_embedding, query_embeddings)
    best_match_idx = scores.argmax()
    value = best_match_idx.item()


    previous_needed_or_not_dict={
        1: True,
        2: False,
        3: False,
        4: False,
        5: True,
        6: False,
    }

    return queries[best_match_idx], scores[0][best_match_idx].item(),value+1,previous_needed_or_not_dict[value+1]

# main function for API calling
def get_L1_board_data(board_name, previous_data_needed_or_not, sprint,person,idx):
    """ pass the board name ,previous_data_needed_or_not , sprint name and the person name to the tool to get the L1 board data 
    Args:
        board_name (str): The name of the board. eg:cdf
        previous_data_needed_or_not (bool): Whether to get the previous data or not. True or False
        sprint (str, optional): The name of the sprint. Defaults to None. eg. sprint 1
        person (str, optional): The name of the person. Defaults to None. eg. manoj
    """
    write_to_checkpoint_file("Crew function called with parameters "+"board_name "+str(board_name)+" sprint_name "+str(sprint)+" person_name "+str(person)+" previous_data_needed_or_not "+str(previous_data_needed_or_not))
 

    if(sprint is None):
        sprint_name = get_current_sprint()
        sprint_id = get_sprint_id(board_name, sprint_name)
    else:
        sprint_id=get_sprint_id(board_name,sprint)

    if(person is not None):
        jql=f"assignee={person}"
    else:
        jql=None

    
    try:
        os.remove("generated_files/current.json")
        os.remove("generated_files/history.json")
        os.remove("generated_files/current.csv")
        os.remove("generated_files/history.csv")
        print("generated_files removed successfully")
    except OSError:
        pass

    if(idx==5):
        Fut_sprints=get_future_sprint_ids(board_name,sprint_id)
        for i in Fut_sprints:
            api_helper(i,jql,"generated_files/current.json")
        json_to_csv("generated_files/current.json","generated_files/current.csv")
    else:
        api_helper(sprint_id,jql,"generated_files/current.json")
        json_to_csv("generated_files/current.json","generated_files/current.csv")

    # If previous data is needed 
    if previous_data_needed_or_not:
        # getting previous 6 sprint id for the given board name , sprintid
        sprint_ids = get_previous_sprint_ids(board_name, sprint_id)
        len_of_historical_sprints=len(sprint_ids)
        for i in sprint_ids:
            api_helper(i,jql,"generated_files/history.json") 
        json_to_csv("generated_files/history.json","generated_files/history.csv")

        # getting the historical data average story points for the last 6 sprints
        df = pd.read_csv("generated_files/history.csv")
        total_sp=(df['story_points'].sum())/len_of_historical_sprints

        return total_sp
    
    return None

# fetching requested_by field from the epic jira endpoint using the parent key
def fetch_requested_by(parent_key: str, cache: dict) -> str:
    """
    Fetch the 'requested_by' field from the Epic Jira endpoint using the parent_key.
    Use a cache to avoid duplicate API calls.
    """
    if parent_key in cache:
        return cache[parent_key]  # Return cached value

    jira_endpoint = f"https://wellsfargo-jira-test.atlassian.net/rest/agile/1.0/issue/{parent_key}"
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')

    headers = {
        'Accept': 'application/json'
    }

    auth = HTTPBasicAuth(email, api_token)
    response = requests.get(jira_endpoint, headers=headers, auth=auth)
    if response.status_code == 200:
        data = response.json()

        with open("generated_files/epic.json", 'w') as f:
            json.dump(data, f, indent=2)

        requested_by = data.get("fields", {}).get("customfield_10043", "Unknown")
        
        if "RTB" in requested_by:
            requested_by = "RTB"
        elif "CTB" in requested_by:
            requested_by = "CTB"

        cache[parent_key] = requested_by  # Store in cache
        return requested_by
    else:
        print("no response from the server")
        cache[parent_key] = "Unknown"  # Store in cache even for failed requests
        return "Unknown"

# RTB/CTB column addition function
def add_rtb_ctb_column(df: pd.DataFrame):
    """
    Add a new column 'requested_by' to the DataFrame by fetching data from the Jira endpoint.
    Use a cache to avoid duplicate API calls.
    """
    cache = {}  # Initialize an empty dictionary for caching
    df['requested_by'] = df['parent_key'].apply(lambda key: fetch_requested_by(key, cache))
    df.to_csv("generated_files/current.csv", index=False) 

#FTE/FTC column addition function
def add_employment_type():
    csv_path = "generated_files/current.csv"
    output_path = "generated_files/current.csv"
    # Define the employment type mapping
    employment_type = {
        "Alice": "FTC",
        "Bob": "FTC",
        "Rishika": "FTE",
        "Hari": "FTE",
        "Apoorva": "FTE",
        "David": "FTC",
        "Pavithra": "FTE",	
        "Alok": "FTE",
        "Peter": "FTC",
        "Sai": "FTE",
        "Krithika": "FTE",
        "Seetha": "FTC",
        "Rasheed": "FTE",
        "Rachin": "FTC",
        "Nitish": "FTE",
        "Noor": "FTE",
        "Khaleel": "FTC",
        "Vikram": "FTC",
        "Dube": "FTE",
        "Ashwin": "FTC",
    }

    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Add a new column 'employment_type' based on the 'assignee' column
    df['employment_type'] = df['assignee'].map(employment_type).fillna("Unknown")

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_path, index=False)

    print(f"Updated file saved to {output_path}")


# leave calculater function for the given person and sprint name
def total_leave_days(name, sprint):
    csv_path='generated_files/PTO.csv'
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().date()
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Filter for the person and sprint (case-insensitive)
    filtered = df[
        (df['name'].str.lower() == name.lower()) &
        (df['sprint'].str.lower() == sprint.lower())
    ]
    
    total_leave_days = filtered['total_days'].sum()

    return total_leave_days

def extract_code_section(input_file, output_file):
    inside_code = False
    extracted_lines = []

    with open(input_file, "r", encoding="utf-8") as file:
        for line in file:
            if "#code start" in line:
                inside_code = True
                continue
            elif "#code end" in line:
                inside_code = False
                break
            if inside_code:
                extracted_lines.append(line)

    with open(output_file, "w", encoding="utf-8") as file:
        file.writelines(extracted_lines)
    print(f"Extracted code section saved to {output_file}")
    # os.remove(input_file)


# Required for PTO data integration
def get_membership_of_board(board:str):
    board_membership={
    "CDF": ["Alice","Bob","Rishika","Hari","Apoorva"],
    "EBSNF": ["Apoorva","David","Pavithra","Alok","Peter"],
    "TES1": ["Sai","Krithika","David"],
    "TES2": ["Seetha","Rasheed","Rachin"],	
    "APS1": ["Nitish","Noor","Khaleel"],
    "APS2": ["Vikram","Dube","Ashwin"],
    }

    return board_membership.get(board.upper(),[])


def clear_empty_labels():
    """
    Clears rows in the 'labels' column where the value is an empty list ([]).
    """
    file_path = "generated_files/current.csv"
    df = pd.read_csv(file_path)
    df.loc[df['labels'] == '[]', 'labels'] = ''  # Replace '[]' with an empty string
    df.to_csv(file_path, index=False)
    print("Cleared rows with empty labels.")

def restore_empty_labels():
    """
    Restores rows in the 'labels' column where the value was cleared (empty string) back to an empty list ([]).
    """
    file_path = "generated_files/current.csv"
    df = pd.read_csv(file_path)
    df.loc[df['labels'] == '', 'labels'] = '[]'  # Replace empty string with '[]'
    df.to_csv(file_path, index=False)
    print("Restored empty labels to [].")