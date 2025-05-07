import os
from crewai import Agent, Task, Crew, LLM
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

# custom imports 
from Main_architecture.Vector_DB.FIASS_Helper import store_queries_in_vector_db,get_most_relevant_query
from Main_architecture.Vector_DB.crew1_db import db1
from Main_architecture.Vector_DB.crew3_db import db2
from Main_architecture.Vector_DB.crew4_db import db3


# Load environment variables
load_dotenv()

# Initialize LLM model
llm = LLM(
    model="sambanova/DeepSeek-R1-Distill-Llama-70B",
    temperature=0.1,
    max_tokens=2048
)

def wrapper_function(dynamic_user):
    # Here you can add any preprocessing or additional logic if needed
    #####################################################################################################################################
    #storing it in vector DB which will be used by Crew1
    query_list1=["1.Sum of all story points assigned to y",
                "2.Total number story points assigned to RTB , CTB seperately in Sprint n",
                "3.Total number of story points assigned to a and b in sprint n seperately",
                "4.All the issues assigned to x in sprint n",
                "5.How is backlog health looking for y board",
                "6.FTE and FTC ratio for total number of story points in sprint n",
                "7.FTE and FTC ratio for total number of story points assigned to y board in sprint n"]


    vector_db1 = store_queries_in_vector_db(query_list1)

    most_similar_query1, similarity_score1 = get_most_relevant_query(vector_db1, dynamic_user, query_list1)

    print(f"Most similar query: {most_similar_query1}")
    # less is better in this case as we are using L2 distance for similarity
    print(f"Similarity score: {similarity_score1}")

    # Query that will give context to crew1
    context1=db1[most_similar_query1[0]]


    ######################################################################################################################################


    # Function to extract code section from agent generated file
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

        #os.remove(input_file)


    # DataFrame structure
    df_structure = """
    The dataset has the following columns:
    - "key": issue key
    - "board": board id to which the issue has been assigned to
    - "summary": summary of issues
    - "description": description of issue
    - "status": ["To Do", "In Progress", "Done"]
    - "assignee": assigned person's name
    - "reporter": reporter's name
    - "acceptance_criteria": acceptance criteria
    - "priority": ["High", "Medium", "Low", "Critical"]
    - "issue_type": ["Story", "Bug", "Task","Defect"]
    - "created": date of creation for the issue (YYYY-MM-DD)
    - "closed": closed date (MM-DD-YYYY) , None if issue is not closed
    - "labels": List of label names
    - "components": List of component names
    - "sprint": sprint name
    - "sprint_state": ["Completed", "Active", "Future"]
    - "sprint_start_date": sprint start date (MM-DD-YYYY)
    - "sprint_end_date": sprint end date (MM-DD-YYYY)
    - "story_points": story points (numeric)
    - "epic_id": epic id 
    - "requested_by": RTB or CTB
    - "employee_type": employee type of assignee ( FTE or FTC )
    """

    df_structure_members ='''
    The dataset has the following columns:
    - "name": name of the employee
    - "L1_Board":L1 board name to which the employee is part of
    - "L2_Board":L2 board name to which the employee is part of
    - "L3_Board":L3 board name to which the employee is part of

    note: a employee can be part of multiple boards...so he can be in multiple rows
    '''

    df_structure_pto = '''
    The dataset has the following columns:
    - "name": name of the employee
    - "leave_type": type of leave taken by employee (PTO, Sick Leave, etc)
    - "start_date": start date of leave (YYYY-MM-DD)
    - "end_date": end date of leave (YYYY-MM-DD)
    - "total_days": duration of leave in days
    - "sprint": sprint name during which the leave was taken
    '''

    class extracted_info(BaseModel):
        data_to_query: str
        specific_need: str



    # Agent 1: Query info extraction
    agent1 = Agent(
        role="User Query analyzer",
        goal="performing the given task to maximum reliability",
        backstory="You are a data expert specializing in analyzing and extracting information from user query",
        llm=llm,
        verbose=True,
    )

    task1 = Task(
        description=f'''
        This is structure of the dataframe:
        {df_structure}

        From the user query {dynamic_user} extract 2 things :
        1. What data has to be queried(data_to_query)
        2. Is there anything specific the user is asking for(specific_need)

        Here are your relevant example to learn from .:
        {context1}
        ''',
        agent=agent1,
        output_pydantic=extracted_info,
        expected_output="A response containing the data_to_query and specific_need.",
    )

    crew0 = Crew(agents=[agent1], tasks=[task1])
    result0 = crew0.kickoff(inputs={"dynamic_user": dynamic_user})
    user_needs = result0["specific_need"]

    with open("generated_files/checkpoint.txt", "a", encoding="utf-8") as f:
        f.write("Date and Time :" + str(datetime.now()) + "\n")
        f.write("users original query :" + dynamic_user + "\n")
        f.write("data to query  :" + result0["data_to_query"] + "\n")
        f.write("specific need  :" + result0["specific_need"] + "\n")
        f.write("------------------------------------------------------------------" + "\n")
    ##############################################################################################################################
    # storing it in vector DB which will be used by Crew3

    query_list2=["1.Sum of all story points assigned to x",
                "2.Total number story points assigned to RTB , CTB seperately in Sprint n",
                "3.Story points assigned to x and y seperately in sprint n",
                "4.Calculate the average story points from the last 2 completed sprints in the y board, then compare the total story points of the next 2 future sprints (one at a time) with this average, and classify each future sprint as 'Underutilized', 'Okay Utilization' (±5 from average), or 'Overutilized",
                "5.FTE and FTC ratio for total number of story points in sprint n",
                "6.FTE and FTC ratio for total number of story points assigned to y board in sprint n seperately"
                ]

    vector_db2 = store_queries_in_vector_db(query_list2)

    most_similar_query2, similarity_score2 = get_most_relevant_query(vector_db2, user_needs, query_list2)

    print(f"Most similar query: {most_similar_query2}")
    # less is better in this case as we are using L2 distance for similarity
    print(f"Similarity score: {similarity_score2}")

    context2=db2[most_similar_query2[0]]

    print(context2)



    # ###############################################################################################################################

    # Agent 2: Pandas query generation
    prompt1 = f"""
        You are an expert in Pandas and data analysis. Convert the following natural language request into a valid Pandas DataFrame query.

        DataFrame Structure:
        {df_structure}

        Request: "{result0['data_to_query']}"

        Ensure the output is a valid Pandas query.
        Just give the valid python code ..no extra comments or print statements needed
        Just giving you a context ..if user asks for backlog it means that sprintState should be Future for that issues no other column is required to find whether a issue is backlog or not
        Encapsulate your output with #code start and #code end
        output should be in this format like only valid python code should be inbetween #code start and #code end like given below
        #code start
        import pandas as pd
        df = pd.read_csv("generated_files/new_custom.csv")

        // your pandas generated code 
        // code saving it into generated_files/output.csv
        #code end 
        Only python valid syntax is allowed inbetween #code start and #code end
        important:please save the filtered dataframe into a file named generated_files/output.csv
        """

    agent2 = Agent(
        role="Pandas Query Agent",
        goal="Generate and execute Pandas queries from user requests.",
        backstory="You are a data expert specializing in analyzing and extracting information from Pandas DataFrames.",
        llm=llm,
        verbose=True,
    )

    task2 = Task(
        description=f"Convert user queries given in {prompt1} into Pandas queries by understanding the dataframe structure given in {prompt1} and return the perfectly working queries",
        agent=agent2,
        expected_output="A pandas query that filters the DataFrame based on the given prompt.",
    )

    crew1 = Crew(agents=[agent2], tasks=[task2])
    result1 = crew1.kickoff(inputs={"prompt1": prompt1})

    with open("generated_files/panda1.py",mode="w",encoding="utf-8") as f:
        f.write("\n")
        f.write(str(result1))
        f.write("\n")

    extract_code_section("generated_files/panda1.py", "generated_files/output1.py")
    os.system("python generated_files/output1.py")
    os.remove("generated_files/panda1.py")


    if user_needs == "None":
        with open('generated_files/output.txt', 'w') as f:
            f.write(f"Nothing to write here as user did not ask anything specific.....\n")
    else:
        prompt2 = f"""
            You are given a CSV file with structure {df_structure}
            Analyze the data and provide a concise pandas code that should run on output.csv file to query the result and also
            to save it in a output.txt file .

            User Query: "{user_needs}"

            Learn from the example below and complete your task:
            {context2}

            #code start
            import pandas as pd
            df = pd.read_csv("generated_files/output.csv")

            // your pandas generated code 
            // code for saving it into generated_files/output.txt with User Query {dynamic_user} Followed by the output
            #code end 
            """

        task3 = Task(
            description=f'''Convert the user query User Query given in {prompt2} into a pandas code by understanding the csv file structure
            to query out specific need of the user and saving it into a text file named output.txt''',
            agent=agent2,
            expected_output="A pandas code to query out specific need of the user and saving it into a text file named output.txt",
        )

        crew2 = Crew(agents=[agent2], tasks=[task3])
        result2 = crew2.kickoff(inputs={"prompt2": prompt2})

        with open("generated_files/panda2.py",mode="w",encoding="utf-8") as f:
            f.write("\n")
            f.write(str(result2))
            f.write("\n")

        extract_code_section("generated_files/panda2.py", "generated_files/output2.py")
        os.remove("generated_files/panda2.py")
        os.system("python generated_files/output2.py")

        prompt3='''
        You are given 2 csv files 
        1. generated_files/members.csv with structure {df_structure_members}
        2. generated_files/PTO.csv with structure {df_structure_pto}
        '''

        agent3 = Agent(
        role="Leave Data Analyst",
        goal="Calculate leave days and adjust workload metrics",
        backstory="Expert in correlating leave data with sprint commitments",
        llm=llm,
        verbose=True    
        )

        task4= Task(
            description=f'''Calculate leave days to give a good idea about the workload based on the leave data provided in the csv files.
            you can find details abt it in {prompt3}. From that learn the csv files available to you , structure pf those csv files 
            and also learn from the relevant examples given in that.''',
            agent=agent3,
            expected_output="A pandas code to calculate leave days for understanding the workload",
        )

        crew3= Crew(agents=[agent3], tasks=[task4])
        result3 = crew3.kickoff(inputs={"prompt3": prompt3})

        with open("generated_files/panda3.py",mode="w",encoding="utf-8") as f:
            f.write("\n")
            f.write(str(result3))
            f.write("\n")

        extract_code_section("generated_files/panda3.py", "generated_files/output3.py")
        os.system("python generated_files/output3.py")
        os.remove("generated_files/panda3.py")









            
        

