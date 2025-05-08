# This ill be the entry file for the L1 level query 
# Standard imports 
import os
from crewai import Agent, Task, Crew, LLM
from pydantic import BaseModel
from dotenv import load_dotenv
import pandas as pd

# custom imports 
from static_files.utils import *
from crews import *
from static_files.hygiene import visualize_missing_data

# main entry point file which will be used by chainLit
async def entrypoint(Query:str) -> str:
    # loading the environment variables from the .env file
    load_dotenv()

    # classify the user query as some predefined categories
    sim_query,sim,idx,previous_needed_or_not=embed_query(Query)

    write_to_checkpoint_file(str(datetime.now()))
    write_to_checkpoint_file("user query is : "+str(Query))
    write_to_checkpoint_file("sim_query is : "+str(sim_query))
    write_to_checkpoint_file("previous_needed_or_not is : "+str(previous_needed_or_not))

    # calling the data getter crew to extract the relevant information from the user query
    result=parameter_extracter_crew(Query)
    board_name=result["board_name"].replace(" ","")
    print("board name is : ",board_name)
    # calling the main API function 
    get_L1_board_data(board_name,previous_needed_or_not,result["sprint_name"],result["person_name"],idx)

    # now we need to add the columns to the dataframe to add the RTB/CTB columns and also FTE/FTC columns
    df=pd.read_csv("generated_files/current.csv")
    add_rtb_ctb_column(df)
    add_employment_type()


    # querying the pandas query crew to get the relevant information from the user query
    if(idx!=6): 
        # excluded JIRA hygiene case
        pandas_query_crew(Query,idx)

    clear_empty_labels()

    # creating the JIRA hygiene dashboard -- common for all the L1 level queries
    visualize_missing_data('generated_files/current.csv', 'outputs/jira_hygiene_dashboard.png')


    # Now integrating the PTO data according to the query
    # data we have is result["board_name"],result["sprint_name"] ( can be none ),result["person_name"] ( can be none )

    board_name=result["board_name"]
    #remove space from the board name
    board_name=board_name.replace(" ","")

    # get the current sprint name if not provided in the query
    if (result["sprint_name"]==None):
        current_sprint_name=get_current_sprint()
        if (idx==5):
            current_sprint_id=get_sprint_id(board_name,current_sprint_name)
            sprint_ids=get_future_sprint_ids(board_name, current_sprint_id)
            sprint_name=[]
            for i in sprint_ids:
                sprint_name.append(get_sprint_name(board_name, i))
        else:
            sprint_name=[current_sprint_name]
    else:
        sprint_name=result["sprint_name"]
    # get the membership of the board if not provided in the query
    if (result["person_name"]==None):
        members=get_membership_of_board(board_name)
    else:
        members=[result["person_name"]]

    if(idx!=6):
        # PTO not required for JIRA hygiene case
        with open("outputs/output.txt", "a") as f:
                flag=0
                for i in members:
                    for j in sprint_name:
                        print(i,j)
                        leaves=total_leave_days(i, j)
                        print("leaves are : ",leaves)
                        if leaves == 0:
                            continue
                        else:
                            flag+=1
                            if flag==1:
                                f.write("\n")
                                f.write(" Here is the required PTO data ")
                                f.write("\n")
                                f.write("---------------------------------------------")
                                f.write("\n")
                            
                        f.write(f"Name: {i} -- Leave days: {leaves} in {j} \n")
                f.write("\n")

    else:
        with open("outputs/output.txt", "w") as f:
           pass
    return "success"





