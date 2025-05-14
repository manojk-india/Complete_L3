```python
import pandas as pd

# Constants
TOTAL_WORKING_DAYS_IN_SPRINT = 10
TOLERANCE = 0.1  # 10% tolerance for utilization

# Load data
df = pd.read_csv("./L1_architecture/generated_files/current.csv")         # already filtered for Hari, CDF, sprint 7
df_history = pd.read_csv("./L1_architecture/generated_files/history.csv") # already filtered
df_pto = pd.read_csv("./L1_architecture/generated_files/PTO.csv")         # PTO data


# Compute story points for current sprint
current_points = df['story_points'].fillna(0).sum()

# Compute average story points from history
if not df_history.empty:
    avg_points = df_history['story_points'].fillna(0).groupby(df_history['sprint']).sum().mean()
    print("avg_points: ",avg_points)
else:
    avg_points = 0
#get list of assignees in the current sprint
assignee= df['assignee'].unique()[0]
#get the list of sprints in the current sprint
sprint = df['sprint'].unique()[0]
#split sprint at the first space and get the rest of the string
sprint = sprint.split(" ", 1)[1]
pto_row = df_pto[(df_pto['name'] == assignee) & (df_pto['sprint'] == sprint)]

if not pto_row.empty:
    total_pto_days = pto_row['total_days'].sum()  
    available_ratio = max(0, (TOTAL_WORKING_DAYS_IN_SPRINT - total_pto_days) / TOTAL_WORKING_DAYS_IN_SPRINT)
    adjusted_avg_points = avg_points * available_ratio
else:
    adjusted_avg_points = avg_points


if adjusted_avg_points == 0:
        utilization_status = "No historical data available for comparison."
elif current_points > adjusted_avg_points * (1 + TOLERANCE):
    utilization_status = "Overutilized"
elif current_points < adjusted_avg_points * (1 - TOLERANCE):
    utilization_status = "Underutilized"
elif abs(current_points - adjusted_avg_points) <= adjusted_avg_points * TOLERANCE:
    utilization_status = "Utilization is on par with historical average."
else:
    utilization_status = "Utilization status could not be determined."
# Output
with open("./L1_architecture/outputs/output.txt", "w") as f:
    f.write(f"Query: Capacity utilization of Apoorva in ABC2 board
")
    f.write(f"Current sprint story points: {current_points}
")
    f.write(f"Average of previous sprints: {avg_points:.2f}
")
    f.write(f"PTO-adjusted average: {adjusted_avg_points:.2f}
")
    f.write(f"Capacity utilization status: {utilization_status}
")
    f.write(f"Ideal story point range: {adjusted_avg_points-adjusted_avg_points * TOLERANCE:.2f} - {adjusted_avg_points+adjusted_avg_points * TOLERANCE:.2f}
")
```