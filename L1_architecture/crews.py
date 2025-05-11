from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from dotenv import load_dotenv
from static_files.utils import *
from static_files.models import *
from static_files.prompts import *
import pandas as pd
from vector_db.db import *

load_dotenv()

# Initialize LLM model from sambanova 
# llm = LLM(
#     model="sambanova/DeepSeek-R1-Distill-Llama-70B",
#     temperature=0.2,
#     max_tokens=2048
# )

# llm=LLM(
#     model="ollama/mistral:7b-instruct-q4_K_M",
#     base_url="http://localhost:11434"
# )

llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
)


############################################################################################ code for parameter getter crew and agents


agent = Agent(
    role="Query analysis expert",
    goal="Extract parameters from user query by understanding the users query clearly",
    backstory="You are an expert at understanding queries about boards, sprints, and people",
    llm=llm,
    verbose=True
)

task = Task(
    description="""
    Given a user query {query}, extract the board name, sprint, and person if present
    Note: Jeera/Jira is not a board name or person name, it is a tool name.""",
    agent=agent,
    output_pydantic=info,
    expected_output="""extracted parameters
    1) board_name: eg cdf 
    2) person_name: eg Hari or None
    3) sprint_name: eg sprint 8 or None
    """
)

def parameter_extracter_crew(query:str) -> None:
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff(inputs={"query": query})
    return result

################################################################################################################################################


# inferences .....
# max to max two files to query -- current date( particular) , history ( maybe ) , avg -- complete done 
    

pandas_agent = Agent(
        role="Pandas Query Agent",
        goal="Generate and execute Pandas queries from user requests and following al the rules.",
        backstory="You are a data expert specializing in analyzing and extracting information through Pandas DataFrames following the rules specified.",
        llm=llm,
        verbose=True,
    )

query_task = Task(
            description="""Convert the user query User Query given in {prompt2} into a pandas code by understanding the csv file structure, example provided and the rules provided.
              and saving it into a text file named outputs/output.txt""",
            agent=pandas_agent,
            expected_output="A pandas code to query out specific need of the user and saving it into a text file named outputs/output.txt",
        )

def pandas_query_crew(query,idx):
    example_code = use_case_examples[idx]
    prompt2 = f"""
        You are a Pandas code generation expert. Use this CSV structure:
        {df_structure_main}
        {example_code}
        **Note** : "DO NOT filter the data for the required board, person and sprint, as the data is already filtered."
        **Rules:**
        1. Do not filter the data for the required board(project_key), person, and sprint, as the data is already filtered.
        2. Write code using the above rules and the example provided. Code should be executable without errors and should look like the example provided.
        3. Always start with `df = pd.read_csv("generated_files/current.csv")`
        4. Never create new DataFrames - only use `df`
        5. For counts: Use vectorized operations like `.sum()` or `len(df)`
        6. For separate results (e.g., RTB/CTB), calculate in one code block
        7. Save results to `outputs/output.txt` with this format:
        - First line: "Query: [user's exact query]"
        - Subsequent lines: Results
        8. Handle nulls appropriately (e.g., `.fillna(0)` for numeric columns)
        9. For date columns: Assume MM-DD-YYYY format unless specified
        10. Enclose the code in triple backticks (```python) and add a comment `#code start` at the beginning and `#code end` at the end

        
        

        **Current Query:** "{query}"
            """
    crew = Crew(agents=[pandas_agent], tasks=[query_task])
    result = crew.kickoff(inputs={"prompt2": prompt2})
    with open("outputs/panda.py", "w") as f:
        f.write(str(result))
    extract_code_section( "outputs/panda.py","outputs/output.py")
    os.system("python outputs/output.py")
    write_to_checkpoint_file("pandas query crew called")


################################################----STORY READINESS CREW-----###########################################################

# Define the evaluation agent
criteria_evaluator = Agent(
    role="Acceptance Criteria Quality Evaluator",
    goal="Evaluate if acceptance criteria is well-documented and understandable by non-technical users",
    backstory="""You are an expert in User Story quality assessment with deep knowledge of 
    acceptance criteria best practices. You specialize in evaluating the clarity, 
    completeness and accessibility of Given/When/Then formatted requirements.""",
    llm=llm,
    verbose=True,
)

# Define the evaluation task with a detailed prompt
evaluation_task = Task(
    description="""
    Note: Just classify ..no function calling is required 
    Evaluate the quality of the following acceptance criteria 
    

    {acceptance_criteria}
    
    By understanding acceptance crieteria and analyzing it do the following 
    #) classification : Well Documented or Not Well Documented
    #) strengths : ["strength1", "strength2"...],
    #) improvement_areas: ["area1", "area2"...],
    #) revised_version: "Proper acceptance crieteria without missing anything in Given When Then format"

    While classifying it as well documented or not consider th below 
    First of all check whether it is in Given When Then format or not...if not directly classify it as Not Well Documented
    Then even if it is Given When Then format .....check whether its written in a wells understandable way and then classify accordingly 
    
    Provide specific feedback on strengths and areas for improvement.

    Even if you feel the acceptance crieteria is okay just classify it as well documneted . only classify it as poor only if you feel it is very poor

    Note : Dont miss out any parameters mentionedd at all.....
    """,
    agent=criteria_evaluator,
    expected_output="""
        "classification": Well Documented or Not Well Documented
        "strengths": ["strength1", "strength2"...],
        "improvement_areas": ["area1", "area2"...],
        "revised_version": "Proper acceptance crieteria without missing anything in Given When Then format"
    """,
    output_pydantic=Evaluated_metrics
)



# Create the crew
acceptance_criteria_crew = Crew(
    agents=[criteria_evaluator],
    tasks=[evaluation_task],
    verbose=True
)

# Function to evaluate acceptance criteria
def evaluate_acceptance_criteria(acceptance_criteria):
    result=acceptance_criteria_crew.kickoff(inputs={"acceptance_criteria": acceptance_criteria})
    return result["classification"], result["strengths"], result["improvement_areas"], result["revised_version"]





# validation function for acceptance criteria 
def process_evaluations():
    """
    Process each row in the CSV file to evaluate acceptance criteria and summaries.
    
    Args:
        csv_file: Path to the input CSV file
        output_csv: Path to save the output CSV file
    """
    csv_file="generated_files/current.csv"
    output_csv="generated_files/current.csv"
    # Load the CSV file with proper error handling
    try:
        df = pd.read_csv(csv_file)
        print(f"Successfully loaded CSV with {len(df)} rows")
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found. Please check the file path.")
        return
    except Exception as e:
        print(f"Error loading CSV: {str(e)}")
        return
    
    # Create empty result columns
    df["acceptance_result"] = ""
    df["acceptance_improvement"] = None
    
    # Process each row
    total_rows = len(df)
    for index, row in df.iterrows():
        try:
            # Progress indicator
            if index % 10 == 0:
                print(f"Processing row {index}/{total_rows}...")
            
            # Skip if required columns are missing
            if pd.isna(row.get('acceptance_crieteria', None)):
                continue
                
            # Evaluate acceptance criteria if present
            if not pd.isna(row.get('acceptance_crieteria', None)):
                acceptance_result = evaluate_acceptance_criteria(row['acceptance_crieteria'])
                df.at[index, "acceptance_result"] = acceptance_result[0]
                df.at[index, "acceptance_improvement"] = {
                    'strengths': acceptance_result[1],
                    'improvement_areas': acceptance_result[2],
                    'revised_version': acceptance_result[3]
                }
                
        except Exception as e:
            print(f"Error processing row {index}: {str(e)}")
    
    # Save to new CSV
    try:
        df.to_csv(output_csv, index=False)
        print(f"Successfully saved results to {output_csv}")
        return output_csv
    except Exception as e:
        print(f"Error saving CSV: {str(e)}")
        return None
    


    