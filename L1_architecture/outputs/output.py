import pandas as pd

# Load current sprint data
df = pd.read_csv("generated_files/current.csv")

# Calculate FTE and FTC story points for APS 2 board
fte_points = df[df['employment_type'] == 'FTE']['story_points'].fillna(0).sum()
ftc_points = df[df['employment_type'] == 'FTC']['story_points'].fillna(0).sum()

# Output results
with open("outputs/output.txt", "w") as f:
    f.write("Query: fte FTC utilisation for APS 2 board\n")
    f.write(f"FTE story points: {fte_points}\n")
    f.write(f"FTC story points: {ftc_points}\n")
