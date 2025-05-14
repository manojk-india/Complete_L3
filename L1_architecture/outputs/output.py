import pandas as pd

df = pd.read_csv("./L1_architecture/generated_files/current.csv")

assignee_name = "Noor"
project_key = "ABC3"

noor_capacity = df[df['assignee'] == assignee_name]['story_points'].sum()

with open("outputs/output.txt", "w") as f:
    f.write(f"Query: What is the capacity of Noor in ABC3 board ?\n")
    f.write(f"Noor's capacity in ABC3 board: {noor_capacity}\n")
