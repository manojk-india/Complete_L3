use_case_examples = {
    1: """
**Note: **" For Story points related query, we need to check the current sprint story points from current.csv and compare it with the average of previous sprints from history.csv."
**Example Query:** "Story points assigned to Hari in CDF board in sprint 3"
#code start
import pandas as pd

# Load data
df = pd.read_csv("generated_files/current.csv")         # current sprint data
df_history = pd.read_csv("generated_files/history.csv") # previous 6 sprints (or fewer)

# Compute total story points for current sprint
current_points = df['story_points'].fillna(0).sum()

# Compute average story points from history
if len(df_history) > 0:
    avg_points = df_history['story_points'].fillna(0).groupby(df_history['sprint']).sum().mean()
else:
    avg_points = 0

# Compare utilization
if avg_points == 0:
    utilization_status = "No historical data available for comparison."
elif current_points > avg_points:
    utilization_status = "Overutilized"
elif current_points < avg_points:
    utilization_status = "Underutilized"
else:
    utilization_status = "Utilization is on par with historical average"

# Output
with open("outputs/output.txt", "w") as f:
    f.write("Query: Story points assigned to Hari in CDF board in sprint 7\n")
    f.write("Current sprint story points: "+str(current_points))
    f.write("Average of previous sprints: "+str(avg_points:.2f))
    f.write(" Capacity utilization status: "+str(utilization_status))
#code end

""",
    2:"""
**Note** : "DO NOT filter the data for the required board, person and sprint, as the data is already filtered. We need to check the current sprint story points for RTB and CTB from current.csv ."

**Example Query:** "RTB/CTB utilization of CDF board in sprint 3"
**Correct Code:**
#code start
import pandas as pd

# Load current sprint data
df = pd.read_csv("generated_files/current.csv")

# Calculate RTB and CTB story points
# data is already filtered for the required board and sprint. So no need to filter again
rtb_points = df[df['requested_by'] == 'RTB']['story_points'].fillna(0).sum()
ctb_points = df[df['requested_by'] == 'CTB']['story_points'].fillna(0).sum()

# Output
with open("outputs/output.txt", "w") as f:
    f.write("Query: RTB/CTB utilization of CDF board in sprint 7\n")
    f.write("RTB story points: "+str(rtb_points))
    f.write("CTB story points: "+str(ctb_points))
#code end

    """ ,
    3: """
**Use Case: RTB/CTB Utilization for a Person in a Sprint**

**Example Query:** "RTB/CTB utilization of Hari in sprint 3"
**Correct Code:**
#code start
import pandas as pd

# Load current sprint data
df = pd.read_csv("generated_files/current.csv")

# Calculate RTB and CTB story points
# data is already filtered for the required board, person and sprint. So no need to filter again
rtb_points = df[df['requested_by'] == 'RTB']['story_points'].fillna(0).sum()
ctb_points = df[df['requested_by'] == 'CTB']['story_points'].fillna(0).sum()

# Output
with open("outputs/output.txt", "w") as f:
    f.write("Query: RTB/CTB utilization of CDF board in sprint 7\n")
    f.write("RTB story points: "+str(rtb_points))
    f.write("CTB story points: "+str(ctb_points))
#code end

    """
    ,
    4: """
**Use Case: FTE/FTC Utilization for a Board in a Sprint**

**Example Query:** "FTE/FTC utilization of CDF board in sprint 3"
**Correct Code:**

#code start
import pandas as pd

# Load current sprint data
df = pd.read_csv("generated_files/current.csv")

# Calculate FTE and FTC story points for the current sprint
fte_points = df[df['work_type'] == 'FTE']['story_points'].fillna(0).sum()
ftc_points = df[df['work_type'] == 'FTC']['story_points'].fillna(0).sum()

# Output results
with open("outputs/output.txt", "w") as f:
    f.write("Query: FTE/FTC utilization of CDF board in sprint 3\n")
    f.write("FTE story points: "+str(fte_points))
    f.write("FTC story points: "+str(ftc_points))
#code end


"""
    ,
    5: """
**Use Case: Backlog Health of a Board **

**Example Query:** "Backlog health for CDF board"
**Note:** " For Backlog health related query, we need to check the story points in each sprint in current.csv and compare it with the average of previous sprints in history.csv."

#code start
import pandas as pd

# Load current sprint data (multiple sprints in current.csv)
df = pd.read_csv("generated_files/current.csv")

# Load historical data for previous sprints
df_history = pd.read_csv("generated_files/history.csv")

# Calculate average velocity from previous sprints (average of total story points completed per sprint)
if len(df_history) > 0:
    avg_velocity = df_history['story_points'].fillna(0).groupby(df_history['sprint']).sum().mean()
else:
    avg_velocity = 0

# Identify the unique sprint names in the current sprint data
unique_sprints = df['sprint'].unique()

# Define thresholds for overutilization and underutilization (e.g., 20 percent difference from average)
threshold_percentage = 0.2
overutilized_threshold = avg_velocity * (1 + threshold_percentage)
underutilized_threshold = avg_velocity * (1 - threshold_percentage)

# Function to check the utilization status
def check_utilization(sprint_points, avg_velocity, overutilized_threshold, underutilized_threshold):
    if sprint_points >= overutilized_threshold:
        return "Overutilized"
    elif sprint_points <= underutilized_threshold:
        return "Underutilized"
    else:
        return "Healthy"

# Calculate story points for each sprint and determine utilization
utilization_results = {}
for sprint in unique_sprints:
    sprint_points = df[df['sprint'] == sprint]['story_points'].fillna(0).sum()
    utilization_results[sprint] = check_utilization(sprint_points, avg_velocity, overutilized_threshold, underutilized_threshold)

# Output results
with open("outputs/output.txt", "w") as f:
    f.write(f"Query: Backlog health for CDF board \n")
    f.write(f"Average velocity from previous sprints: "+str(avg_velocity:.2f))
    
    for sprint, utilization in utilization_results.items():
        sprint_points = df[df['sprint'] == sprint]['story_points'].fillna(0).sum()
        f.write("str(sprint)+" story points:" +str(sprint_points))
        f.write("str(sprint)+" backlog status:"+str(utilization))

#code end


""",
    6: """
**Use Case: Jira Hygiene for a Board in Current Sprint**

**Example Query:** "Jira hygiene for CDF board"
**Correct Code:**
#code start
#code end

""",
   

}