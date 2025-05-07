import pandas as pd
# Load the dataset
df = pd.read_csv("generated_files/output.csv")

# Filter issues where assignee is Hari and sprint is Sprint 8
hari_sprint8_issues = df[(df['assignee'] == 'Hari') & (df['sprint'] == 'Sprint 8')]

# Calculate total story points assigned to Hari in Sprint 8
total_story_points = hari_sprint8_issues['story_points'].sum()

# Save the result to a text file
with open("generated_files/output.txt", "w") as f:
    f.write(f"Number of story points assigned to Hari in Sprint 8: {total_story_points}")
