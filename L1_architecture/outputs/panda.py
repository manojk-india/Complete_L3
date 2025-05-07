Here is the complete pandas code to generate the backlog health report for the CDF board:

```python
#code start
import pandas as pd

# Load current sprint data
df = pd.read_csv("generated_files/current.csv")

# Load historical data for previous sprints
df_history = pd.read_csv("generated_files/history.csv")

# Calculate average velocity from previous sprints
if len(df_history) > 0:
    avg_velocity = df_history['story_points'].fillna(0).groupby(df_history['sprint']).sum().mean()
else:
    avg_velocity = 0

# Identify unique sprints in current data
unique_sprints = df['sprint'].unique()

# Define utilization thresholds (20% difference from average)
threshold_percentage = 0.2
overutilized_threshold = avg_velocity * (1 + threshold_percentage)
underutilized_threshold = avg_velocity * (1 - threshold_percentage)

# Function to determine utilization status
def check_utilization(sprint_points, avg_velocity, overutilized_threshold, underutilized_threshold):
    if sprint_points >= overutilized_threshold:
        return "Overutilized"
    elif sprint_points <= underutilized_threshold:
        return "Underutilized"
    else:
        return "Healthy"

# Calculate story points and utilization for each sprint
utilization_results = {}
for sprint in unique_sprints:
    sprint_points = df[df['sprint'] == sprint]['story_points'].fillna(0).sum()
    utilization_results[sprint] = check_utilization(sprint_points, avg_velocity, overutilized_threshold, underutilized_threshold)

# Save results to output file
with open("outputs/output.txt", "w") as f:
    f.write(f"Query: Backlog health for Cdf board\n")
    f.write(f"Average velocity from previous sprints: {avg_velocity:.2f}\n")
    for sprint, utilization in utilization_results.items():
        sprint_points = df[df['sprint'] == sprint]['story_points'].fillna(0).sum()
        f.write(f"{sprint} - Story points: {sprint_points}\n")
        f.write(f"{sprint} - Backlog status: {utilization}\n")

#code end
```