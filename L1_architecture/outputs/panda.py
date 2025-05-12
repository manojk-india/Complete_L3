```python
#code start
import pandas as pd

# Load current sprint data
df = pd.read_csv("./L1_architecture/generated_files/current.csv")

# Calculate FTE and FTC story points for the current sprint
fte_points = df[df['employment_type'] == 'FTE']['story_points'].fillna(0).sum()
ftc_points = df[df['employment_type'] == 'FTC']['story_points'].fillna(0).sum()

# Output results
with open("./L1_architecture/outputs/output.txt", "w") as f:
    f.write("Query: FTE/FTC utilization of abc1 board in sprint 9\n")
    f.write("FTE story points: "+str(fte_points)+"\n")
    f.write("FTC story points: "+str(ftc_points)+"\n")
#code end
```