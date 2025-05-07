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
llm = LLM(
    model="sambanova/DeepSeek-R1-Distill-Llama-70B",
    temperature=0.2,
    max_tokens=2048
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
    description="""Given a user query {query}, extract the board name, sprint, and person if present""",
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

