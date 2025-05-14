import pandas as pd

# Load current sprint data
df = pd.read_csv("./L1_architecture/generated_files/current.csv")

# Calculate RTB and CTB story points
# data is already filtered for the required board and sprint. So no need to filter again
rtb_points = df[df['requested_by'] == 'RTB']['story_points'].fillna(0).sum()
ctb_points = df[df['requested_by'] == 'CTB']['story_points'].fillna(0).sum()

# Output
with open("./L1_architecture/outputs/output.txt", "w") as f:
    f.write("Query: RTB/CTB classification for ABC2 board\n")
    f.write("RTB story points: "+str(rtb_points)+"\n")
    f.write("CTB story points: "+str(ctb_points))
