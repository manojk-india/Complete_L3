# all import statments 
from crewai import Crew, Process,Agent,Task,LLM
from pydantic import BaseModel
from dotenv import load_dotenv
import pandas as pd
from typing import List
import os


# importing custom objects 
from Main_architecture.prompt import prompt2,prompt3,prompt4,prompt5
from Main_architecture.agents import English_expert,Jira_expert
from Main_architecture.tasks import Splitter1,Splitter2,Multiplier,should_go_down_or_not,should_we_go_to_L1_or_L2
from Main_architecture.pdf_creator import *
from Main_architecture.utils import *


# calling the L1 architecture 
from L1_architecture.entry import entrypoint
from L2_architecture.main import *


# Load environment variables
load_dotenv()

# Initialize LLM model here
# llm = LLM(
#     model="sambanova/DeepSeek-R1-Distill-Llama-70B",
#     temperature=0.1,
#     max_tokens=2048
# )

llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
)

# main function at L3 level , we have to modify for handling case insensitive queries -- voice input 
async def main_L3_query(query:str):

    # clearing the output file
    with open("outputs/output.txt", mode="w") as file:
        pass

    # temp will be our final file 
    delete_files(["outputs/final.pdf","outputs/final2.pdf","outputs/temp.pdf"])



    # board architecture
    L1=["ABC1","ABC2","ABC3","ABC4","ABC5","ABC5"]
    L2=["DEF1","DEF2","DEF3"]
    L3=["GHI"]

    # classifying the query as L1 or L2 or L3
    if any(item in query for item in L3):
        level="L3"
    elif any(item in query for item in L2):
        level="L2"
    else:
        level="L1"
    # write_into_checkpoint_file("LEVEL:"+level)

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
        
    # L1 query
    if ( level == "L1"):
        boards,name,time_period=info_extractor(prompt2,query)

        if len(boards)==0:
            boards=get_person_boards(name[0])

        if(len(boards)>1):
            # we have to split the query into multiple queries
            queries2=query_multiplier(boards,name,query,prompt3)
        else:
            # len of board is for sure 1 no other option then number of people might be 0
            queries2=[query]

        write_into_checkpoint_file([" Inside main l1 condition. boards of interest are : "+str(boards),"name identified is : "+str(name),"time period is : "+str(time_period)])
        write_into_checkpoint_file(["Multiplied queries are : "])
        write_into_checkpoint_file(queries2)
        write_into_checkpoint_file(["-----------------------------------"])
        # here all ready -- modify and call the architecture built

        for j in queries2:
            # here all ready -- modify and call the architecture built
            # only constraint is j should contain L1 board name 
            entrypoint(j)

            with open("L1_architecture/outputs/output.txt", mode="r") as file:
                output = file.read()

            with open("outputs/output.txt", mode="a") as file:
                file.write(f"{j}")
                file.write(output)
                file.write("------------------------------------------------------------------------")

            try:
                create_pdf("outputs/temp.pdf",
                            "L1_architecture/outputs/jira_hygiene_dashboard.png",
                            "L1_architecture/outputs/output.txt",
                            "L1_architecture/generated_files/current.csv")
            except Exception as e:
                print(e)

            if os.path.exists("L1_architecture/outputs/acceptance_crieteria_report.pdf"):
                merge_pdfs("outputs/temp.pdf","L1_architecture/outputs/acceptance_crieteria_report.pdf", "outputs/final.pdf")
                os.remove("outputs/temp.pdf")
                os.rename("outputs/final.pdf","outputs/temp.pdf")
    

    elif( level == "L2"):
        should_go_down_or_not_flag=go_down_or_not(prompt4,query)

        write_into_checkpoint_file([" Inside main L2 condition. Should we go down or not : "+str(should_go_down_or_not_flag)])


        # staying in the L2 level 
        if not should_go_down_or_not_flag:
            # changing the architecture and calling it here -- here sprint is not relevant -- RTB/CTB and feature readiness
            t=L2_entry_point(query)

            with open("L2_architecture/Report/output.txt", mode="r") as file:
                    output = file.read()

            with open("outputs/output.txt", mode="a") as file:
                file.write(f"{j}")
                file.write(output)
                file.write("\n")


            if(t=="feature_readiness"):
                create_structured_pdf_feature("outputs/temp.pdf","L2_architecture/Report/output.txt", "L2_architecture/Report/missing_values_dashboard.png", 
                  "L2_architecture/Report/Bad_values_dashboard.png",
                  "L2_architecture/data/Final_API.csv", "L2_architecture/Report/acceptance_report.pdf", 
                  "L2_architecture/Report/summary_report.pdf")
            else:
                create_and_append_pdf_RTBCTB("L2_architecture/Report/output.txt","L2_architecture/Report/missing_values_dashboard.png"
                      ,"L2_architecture/data/API.csv", "outputs/temp.pdf")
        else:
            # going down to L1 level
            board,name,time_period=info_extractor(prompt2,query)

            # function call to find boards under the L2 board
            if name:
                boards=board_under_L2_board(board[0],name[0])
            else:
                boards=board_under_L2_board(board[0],None)

            write_into_checkpoint_file(["Interest boards under L2 board  : "+str(boards),"Name of the person is : "+str(name),"time period is : "+str(time_period)])


            queries2=query_multiplier(boards,name,query,prompt3)

            write_into_checkpoint_file(["Multiplied queries are"])
            write_into_checkpoint_file(queries2)
            write_into_checkpoint_file(["-----------------------------------"])

            for j in queries2:
                # here we will get the L2 queries one by one 
                entrypoint(j) 
                with open("L1_architecture/outputs/output.txt", mode="r") as file:
                    output = file.read()

                with open("outputs/output.txt", mode="a") as file:
                    file.write(f"{j}")
                    file.write(output)
                    file.write("\n")
                try:
                    create_pdf("outputs/temp.pdf",
                                "L1_architecture/outputs/jira_hygiene_dashboard.png",
                                "L1_architecture/outputs/output.txt",
                                "L1_architecture/generated_files/current.csv")
                except Exception as e:
                    print(e)

                if os.path.exists("L1_architecture/outputs/acceptance_crieteria_report.pdf"):
                    merge_pdfs("outputs/temp.pdf","L1_architecture/outputs/acceptance_crieteria_report.pdf", "outputs/final.pdf")
                    os.remove("outputs/temp.pdf")
                    os.rename("outputs/final.pdf","outputs/temp.pdf")


    else:
        # This is a L3 level query
        where_to_go=L1_or_L2(prompt5,query)
        write_into_checkpoint_file(["Inside main L3 condition. Where should we go to L1 or L2 level: "+str(where_to_go)])
        print("where to go : ",where_to_go)
        if where_to_go=="L2 level": 
            # now we have boards , query and name =[]...
            write_into_checkpoint_file(["Going down to L2 from L3 level"])

            boards=L2
            queries2=query_multiplier(boards,[],query,prompt3)
            for j in queries2:
                t=L2_entry_point(j)

                with open("L2_architecture/Report/output.txt", mode="r") as file:
                        output = file.read()

                with open("outputs/output.txt", mode="a") as file:
                    file.write(f"{j}")
                    file.write(output)
                    file.write("\n")


                if(t=="feature_readiness"):
                    create_structured_pdf_feature("outputs/temp.pdf","L2_architecture/Report/output.txt", "L2_architecture/Report/missing_values_dashboard.png", 
                    "L2_architecture/Report/Bad_values_dashboard.png",
                    "L2_architecture/data/Final_API.csv", "L2_architecture/Report/acceptance_report.pdf", 
                    "L2_architecture/Report/summary_report.pdf")
                else:
                    create_and_append_pdf_RTBCTB("L2_architecture/Report/output.txt","L2_architecture/Report/missing_values_dashboard.png"
                        ,"L2_architecture/data/API.csv", "outputs/temp.pdf")


        else:
            # we have to go down to L1 level 
            write_into_checkpoint_file(["Going down to L1 from L3 level"])
            boards=L1
            queries2=query_multiplier(boards,[],query,prompt3)
            for j in queries2:
                entrypoint(j) 
                with open("L1_architecture/outputs/output.txt", mode="r") as file:
                    output = file.read()

                with open("outputs/output.txt", mode="a") as file:
                    file.write(f"{j}")
                    file.write(output)
                    file.write("\n")
                try:
                    create_pdf("outputs/temp.pdf",
                                "L1_architecture/outputs/jira_hygiene_dashboard.png",
                                "L1_architecture/outputs/output.txt",
                                "L1_architecture/generated_files/current.csv")
                except Exception as e:
                    print(e)

                if os.path.exists("L1_architecture/outputs/acceptance_crieteria_report.pdf"):
                    merge_pdfs("outputs/temp.pdf","L1_architecture/outputs/acceptance_crieteria_report.pdf", "outputs/final.pdf")
                    os.remove("outputs/temp.pdf")
                    os.rename("outputs/final.pdf","outputs/temp.pdf")


        

        



    write_into_checkpoint_file(["------------------------------------------------------------------------------------------------ Operation over "])


            

            

            






        
            







