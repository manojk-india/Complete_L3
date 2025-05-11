use_case_examples = {
    1: """
**Note: **" For capacity utilization related query, we need to check the current sprint story points from current.csv and compare it with the average of previous sprints from history.csv also considering the PTO.csv and threshold as done in the code below."
**Example Query:** "What is the capacity utilization of Hari in CDF board in sprint 7"
#code start
import pandas as pd

# Constants
TOTAL_WORKING_DAYS_IN_SPRINT = 10
TOLERANCE = 0.1  # 10% tolerance for utilization

# Load data
df = pd.read_csv("generated_files/current.csv")         # already filtered for Hari, CDF, sprint 7
df_history = pd.read_csv("generated_files/history.csv") # already filtered
df_pto = pd.read_csv("generated_files/PTO.csv")         # PTO data


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
with open("outputs/output.txt", "w") as f:
    f.write(f"Query: Story points assigned to {assignee} in CDF board in sprint {sprint}\n")
    f.write(f"Current sprint story points: {current_points}\n")
    f.write(f"Average of previous sprints: {avg_points:.2f}\n")
    f.write(f"PTO-adjusted average: {adjusted_avg_points:.2f}\n")
    f.write(f"Capacity utilization status: {utilization_status}\n")
    f.write(f"Ideal story point range: {adjusted_avg_points-adjusted_avg_points * TOLERANCE:.2f} - {adjusted_avg_points+adjusted_avg_points * TOLERANCE:.2f}\n")

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
        sprint=sprint.split(" ", 1)[1]
        f.write("str(sprint)+" story points:" +str(sprint_points))
        f.write("str(sprint)+" backlog status:"+str(utilization))
        f.write(" Below you can find low quality acceptance crieteria report ")

#code end


""",
    7: """
**Use Case: Story points use case**

**Example Query:** "Story points assigned to Hari in CDF board in sprint 9"
**Correct Code:**
#code start
import pandas as pd

# Load data
df = pd.read_csv("generated_files/current.csv")         # current sprint data

# Compute total story points for in df dataframe
current_points = df['story_points'].fillna(0).sum()

# Output
with open("outputs/output.txt", "w") as f:
    f.write("Query: Story points assigned to Hari in CDF board in sprint 9 is "+str(current_points))
    f.write("\n")

#code end

""",
   

}