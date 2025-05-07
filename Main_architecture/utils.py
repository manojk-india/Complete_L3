# static functions 
from typing import List
import pandas as pd
from datetime import datetime, timedelta

# in hold -- not used upto now
def get_previous_sprints(today=None):
    # Use today's date if not provided
    if today is None:
        today = datetime.today().date()
    else:
        today = today.date()

    sprint_start = datetime(2025, 1, 1).date()
    sprint_length = 14
    sprints = []
    
    # Generate all sprints for 2025
    sprint_num = 1
    while sprint_start.year == 2025:
        sprint_end = sprint_start + timedelta(days=sprint_length - 1)
        sprints.append({
            "name": f"Sprint {sprint_num}",
            "start": sprint_start,
            "end": sprint_end
        })
        sprint_start += timedelta(days=sprint_length)
        sprint_num += 1

    # Find the sprint today falls into (or the next one after it)
    current_sprint_index = None
    for i, sprint in enumerate(sprints):
        if sprint["start"] <= today <= sprint["end"]:
            current_sprint_index = i
            break
        elif today < sprint["start"]:
            current_sprint_index = i
            break
    if current_sprint_index is None:
        current_sprint_index = len(sprints)

    # Get previous 6 sprint names
    start_index = max(0, current_sprint_index - 6)
    return [s["name"] for s in sprints[start_index:current_sprint_index]]





def get_person_boards(name: str) -> List[str]:
    """
    Retrieve unique boards associated with a person from CSV data.
    
    Args:
        name: Person's name to search (case insensitive)
        csv_path: Path to membership CSV file
        
    Returns:
        List of unique board names (empty list if no matches)
    """

    # Read CSV data
    df = pd.read_csv("generated_files/members.csv")
    
    # Filter and extract boards (case-insensitive match)
    return df.loc[
        df['name'].str.lower() == name.strip().lower(),
        'L1_Board'
    ].unique().tolist()

def board_under_L2_board(board: str,person: str = None) -> List[str]:
    """
    Retrieve all L2 boards associated with a given board from CSV data.
    
    Args:
        board: Board name to search (case insensitive)
        csv_path: Path to membership CSV file
        
    Returns:
        List of unique L2 board names (empty list if no matches)
    """
    assignees={
    "CDF": ["Alice","Bob","Rishika","Hari","Apoorva"],
    "EBSNF": ["Apoorva","David","Pavithra","Alok","Peter"],
    "TES1": ["Sai","Krithika","David"],
    "TES2": ["Seetha","Rasheed","Rachin"],	
    "APS1": ["Nitish","Noor","Khaleel"],
    "APS2": ["Vikram","Dube","Ashwin"],
    }   

    if(board=="APS"):
        Boards = ["APS1","APS2"]
    elif(board=="TES"):
        Boards = ["TES1","TES2"]
    else:
        Boards = ["CDF","EBSNF"]

    if ( person is None):
        return Boards
    else:
        boards_that_person_is_part_of=[]
        for board in Boards:
            if person in assignees[board]:
                boards_that_person_is_part_of.append(board)
        return boards_that_person_is_part_of
    


        

def write_into_checkpoint_file(data: list[str]) -> None:
    """
    Write data into a checkpoint file.
    
    Args:
        data: Data to write into the file
        file_path: Path to the checkpoint file
        
    Returns:
        None
    """
    
    with open("main_checkpoints.txt", "a") as f:
        for item in data:
            f.write(item + "\n")