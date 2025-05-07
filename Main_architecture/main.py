# all import statments 
from crewai import Crew, Process,Agent,Task,LLM
from pydantic import BaseModel
from dotenv import load_dotenv
import pandas as pd
from typing import List
import os


# importing custom objects 
from prompt import prompt1,prompt2,prompt3,prompt4,prompt5
from agents import English_expert,Jira_expert
from tasks import Splitter1,Splitter2,Multiplier,should_go_down_or_not,should_we_go_to_L1_or_L2
from utils import get_person_boards,board_under_L2_board,write_into_checkpoint_file
from Main_architecture.crew import wrapper_function


# calling the L1 architecture 
from L1_architecture.entry import entrypoint


# Load environment variables
load_dotenv()

# Initialize LLM model
llm = LLM(
    model="sambanova/DeepSeek-R1-Distill-Llama-70B",
    temperature=0.1,
    max_tokens=2048
)

# main function at L3 level
def main_L3_query(query:str):

    # board architecture
    L1=["TES1","TES2","CDF","EBSNF","APS1","APS2"]
    L2=["APS","DIS","TES"]
    L3=["Transaction processing"]

    # classifying the query as L1 or L2 or L3
    if any(item in query for item in L3):
        level="L3"
    elif any(item in query for item in L2):
        level="L2"
    else:
        level="L1"




    # crew functions 
    def query_decomposer(prompt,query):
        crew=Crew(agents=[English_expert],tasks=[Splitter1],processes=Process.sequential)
        result=crew.kickoff(inputs={"query":query,"prompt":prompt})
        return result["query"]

    def info_extractor(prompt,query):
        crew=Crew(agents=[English_expert],tasks=[Splitter2],processes=Process.sequential)
        result=crew.kickoff(inputs={"query":query,"prompt2":prompt})
        return result["boards"],result["name"],result["time_period"]

    def query_multiplier(boards,name,query,prompt):
        crew=Crew(agents=[English_expert],tasks=[Multiplier],processes=Process.sequential)
        result=crew.kickoff(inputs={"boards":boards,"name":name,"query":query,"prompt3":prompt})
        return result["query"]

    def go_down_or_not(prompt,query):
        crew=Crew(agents=[Jira_expert],tasks=[should_go_down_or_not],processes=Process.sequential)
        result=crew.kickoff(inputs={"query":query,"prompt4":prompt})
        return result["value"]

    def L1_or_L2(prompt,query):
        crew=Crew(agents=[Jira_expert],tasks=[should_we_go_to_L1_or_L2],processes=Process.sequential)
        result=crew.kickoff(inputs={"query":query,"prompt5":prompt})
        return result["level"]

    # decomposing the query into individual queries
    queries1=query_decomposer(prompt1,query)

    # checkpoint file for better inspection of the flow
    write_into_checkpoint_file(["query is : "+query,"Intial level is : "+level,"queries splitted are : "+str(queries1)])
    write_into_checkpoint_file(["-----------------------------------"])
        
    # L1 query
    if ( level == "L1"):
        for i in queries1:
            write_into_checkpoint_file(["Sub Query is : "+i])
            boards,name,time_period=info_extractor(prompt2,i)

            if len(boards)==0:
                boards=get_person_boards(name[0])

            if(len(boards)>1):
                # we have to split the query into multiple queries
                queries2=query_multiplier(boards,name,i,prompt3)
            else:
                # len of board is for sure 1 no other option then number of people might be 0
                queries2=[i]

            write_into_checkpoint_file(["boards of intrest are : "+str(boards),"name indentified is : "+str(name),"time period is : "+str(time_period)])
            write_into_checkpoint_file(["Multiplied queries are : "])
            write_into_checkpoint_file(queries2)
            write_into_checkpoint_file(["-----------------------------------"])
            # here all ready -- modify and call the architecture built

            for j in queries2:
                # here all ready -- modify and call the architecture built
                # only constraint is j should contain L1 board name 
                entrypoint(j)

                # code for taking the outputs and saving it in the output.pdf file 


    elif( level == "L2"):
        for i in queries1:
            write_into_checkpoint_file(["Sub Query is : "+i])
            should_go_down_or_not_flag=go_down_or_not(prompt4,i)

            write_into_checkpoint_file(["Should we go down or not : "+str(should_go_down_or_not_flag)])


            # staying in the L2 level 
            if not should_go_down_or_not_flag:
                # changing the architecture and calling it here -- here sprint is not relevant
                pass
            else:
                # going down to L1 level
                board,name,time_period=info_extractor(prompt2,i)

                # function call to find boards under the L2 board
                boards=board_under_L2_board(board[0],name[0])

                write_into_checkpoint_file(["Intrest boards under L2 board  : "+str(boards),"Name of the person is : "+str(name),"time period is : "+str(time_period)])

                if len(boards)==0:
                    continue

                queries2=query_multiplier(boards,name,i,prompt3)

                write_into_checkpoint_file(["Multiplied queries are"])
                write_into_checkpoint_file(queries2)
                write_into_checkpoint_file(["-----------------------------------"])

                for j in queries2:
                    # here all ready -- modify and call the architecture built
                    wrapper_function(j)

    else:
        # This is a L3 level query
        for i in queries1:
            where_to_go=L1_or_L2(prompt5,i)
            write_into_checkpoint_file(["Where should we go to L1 or L2 level: "+str(where_to_go)])

            if where_to_go=="L2 level": 
                # now we have boards , query and name =[]...
                boards=L2
            else:
                # we have to go down to L1 level 
                boards=L1

            query=i
            queries2=query_multiplier(boards,[],query,prompt3)
            write_into_checkpoint_file(["Multiplied queries are : "])
            write_into_checkpoint_file(queries2)
            write_into_checkpoint_file(["-----------------------------------"])

            for j in queries2:
                # here all ready -- modify and call the architecture built
                wrapper_function(j)



    write_into_checkpoint_file(["------------------------------------------------------------------------------------------------ Operation over "])


            

            

            






        
            







