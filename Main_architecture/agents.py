from crewai import Crew, Process,Agent,Task,LLM
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# # Initialize LLM model
# llm = LLM(
#     model="sambanova/DeepSeek-R1-Distill-Llama-70B",
#     temperature=0.1,
#     max_tokens=2048
# )

llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
    function_call_behavior="auto"
)


English_expert = Agent(
    role="Expert in language of English",
    goal="Understand and analyze English language queries",
    backstory="Expert in analyzing technical queries and retreiving data from it",
    llm=llm
)

Jira_expert = Agent(
    role="Expert in Jira",
    goal="Understand and analyze Jira queries",
    backstory="Expert in analyzing technical queries and understanding its intricacies",
    llm=llm
)




