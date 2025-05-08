<think>
Okay, I need to generate a pandas code based on the user's query. The user asked for "fte FTC utilisation for APS 2 board". Let me break this down.

First, I look at the CSV structure provided. The columns include 'project_key' which is the board name, 'employment_type' which can be FTE or FTC, and 'story_points' which is numeric. 

The example code given loads the CSV, calculates FTE and FTC story points, and writes the results to a file. I should follow that structure.

I notice the user's query doesn't specify a sprint, so I don't need to filter by sprint. Also, the note says not to filter data as it's already done, so I can proceed without additional filtering.

I'll start by importing pandas and loading the CSV. Then, I'll calculate the sum of story points for FTE and FTC using boolean indexing. I should handle nulls with fillna(0) to avoid errors.

Finally, I'll write the query and results to outputs/output.txt, ensuring the format matches the example.

I think that's all. Now, I'll write the code accordingly.
</think>

```python
#code start
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
#code end
```