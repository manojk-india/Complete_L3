from crewai import Crew, Process,Agent,Task,LLM
from models import queries,info,going_down_or_not,where_should_we_go
from agents import English_expert,Jira_expert
       

Splitter1=Task(
  description="Take user query {query} and decompose it into individual tasks by learning from the {prompt}",
  expected_output="List of queries to be solved by agents",
  output_pydantic=queries,
  agent=English_expert
)

Splitter2 = Task(
  description="""Take user query {query} and understand {prompt2} to extract the below information from it
  1. List of boards mentioned in the query if any else None
  2. name of the person mentioned in the query if any else None
  3. Is the time period mentioned in the query -- True or False""",
  expected_output="List of boards, name of person, time period( bool value)",
  output_pydantic=info,
  agent=English_expert
)

Multiplier=Task(
    description="""Take the {boards} ,{name} of the person and {query} and understand {prompt3} 
    to create multiple queries, no function calling is required, just understand the inputs and create the queries""",
    expected_output="List of queries to be solved by agents",
    output_pydantic=queries,
    agent=English_expert
)

should_go_down_or_not=Task(
    description=""" Take the user query {query} and understand {prompt4} to decide whether to go down the hierarchy or not""",
    expected_output="Boolean value stating whether to go down the hierarchy or not, dont use any function calling ... just understand the inputs and create the queries",
    output_pydantic=going_down_or_not,
    agent=English_expert
)

should_we_go_to_L1_or_L2=Task(
    description=""" Take the user query {query} and understand {prompt5} to decide whether to go down to L1 level or L2 level
    dont use any function calling ... just understand the inputs and create the queries",""",
    expected_output="Value denoting L1 level or L2 level ",
    output_pydantic=where_should_we_go,
    agent=English_expert
)