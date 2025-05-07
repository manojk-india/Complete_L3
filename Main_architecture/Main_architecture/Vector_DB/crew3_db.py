# here we are creating a database of queries and their corresponding data to query and specific needs in the form of a dictionary.

db2={
    "1":'''specific_need: Sum of all story points assigned to x then 
         code for reference: 
         #code start
         import pandas as pd
         # Load the dataset
         df = pd.read_csv("generated_files/output.csv")

         # Filter issues assigned to David
         x_issues = df[df['assignee'] == 'x']

         # Calculate the total story points assigned to David
         total_story_points = x_issues['story_points'].sum()

         # Write the result to a text file
         with open("generated_files/output.txt", "w") as f:
            f.write(f"Total story points assigned to x "+str(total_story_points))
         #code end

         ''',

    "2":'''specific_need: Total number story points assigned to RTB , CTB seperately in Sprint n then 
         code for reference: 
            #code start

            import pandas as pd
            # Load the dataset
            df = pd.read_csv("generated_files/output.csv")

            # Filter issues for Sprint n assigned to RTB
            rtb_sprintn_issues = df[(df['requested_by'] == 'RTB') & (df['sprint'] == 'Sprint n')]
            total_story_points_rtb = rtb_sprintn_issues['story_points'].sum()

            # Filter issues for Sprint n assigned to CTB
            ctb_sprintn_issues = df[(df['requested_by'] == 'CTB') & (df['sprint'] == 'Sprint n')]
            total_story_points_ctb = ctb_sprintn_issues['story_points'].sum()

            # Calculate total story points in Sprint n
            total_story_points_sprintn = total_story_points_rtb + total_story_points_ctb

            # Calculate percentages for RTB and CTB
            rtb_percentage = (total_story_points_rtb / total_story_points_sprintn) * 100 if total_story_points_sprintn > 0 else 0
            ctb_percentage = (total_story_points_ctb / total_story_points_sprintn) * 100 if total_story_points_sprintn > 0 else 0

            # Save results to a text file
            with open("generated_files/output.txt", "w") as f:
                  f.write(f"Total story points assigned to RTB in Sprint n"+str(total_story_points_rtb))
                  f.write(f"Total story points assigned to CTB in Sprint n"+str(total_story_points_ctb))
                  f.write(f"Total story points in Sprint n:"+str(total_story_points_sprintn))
                  f.write(f"Percentage of RTB story points:"+str(rtb_percentage:.2f)+"%")
                  f.write(f"Percentage of CTB story points:"+str(ctb_percentage:.2f)+"%")
            #code end
         ''',

    "3":'''specific_need:  Story points assigned to x and y seperately in sprint n then 
          code for reference: 
          #code start
            import pandas as pd

            # Load the dataset
            df = pd.read_csv("generated_files/output.csv")

            # Filter issues assigned to x in Sprint n
            x_issues = df[(df['assignee'] == 'x') & (df['sprint'] == 'Sprint n')]
            total_story_points_x = x_issues['story_points'].sum()

            # Filter issues assigned to y in Sprint n
            y_issues = df[(df['assignee'] == 'y') & (df['sprint'] == 'Sprint n')]
            total_story_points_y = y_issues['story_points'].sum()

            # Calculate total story points for Sprint n
            total_story_points_sprintn = total_story_points_x + total_story_points_y

            # Calculate percentage contribution for x and y
            x_percentage = (total_story_points_x / total_story_points_sprintn) * 100 if total_story_points_sprintn > 0 else 0
            y_percentage = (total_story_points_y/ total_story_points_sprintn) * 100 if total_story_points_sprintn > 0 else 0

            # Save results to a text file
            with open("generated_files/output.txt", "w") as f:
                  f.write(f"Total story points assigned to x in Sprint n"+str(total_story_points_x))
                  f.write(f"Total story points assigned to y in Sprint n"+str(total_story_points_y))
                  f.write(f"Total story points assigned to x and y in Sprint n"+str(total_story_points_sprintn))
                  f.write(f"Percentage contribution of x:"+str(x_percentage:.2f)+"%")
                  f.write(f"Percentage contribution of y:"+str(y_percentage:.2f)+"%")
            #code end
          ''',

    "4":''' specific_need: Calculate the average story points from the last 2 completed sprints in the y board, 
          then compare the total story points of the next 2 future sprints (one at a time) with this average, 
          and classify each future sprint as 'Underutilized', 'Okay Utilization' (±5 from average), or 'Overutilized then

          code for reference: 
            #code start
            import pandas as pd
            # Load the dataset
            df = pd.read_csv("generated_files/output.csv")

            # Step 1: Filter issues by y board
            y_issues = df[df["board"] == "y"]

            # Step 2: Filter completed sprints and sort by end date
            completed_sprints = y_issues[y_issues["sprint_state"] == "Completed"]
            completed_sprints = completed_sprints.sort_values("sprint_end_date", ascending=False)

            # Get last two completed sprints
            last_two_completed_sprints = completed_sprints["sprint"].unique()[:2]

            # Step 3: Calculate average story points for completed sprints
            avg_story_points = (
            completed_sprints[completed_sprints["sprint"].isin(last_two_completed_sprints)]
            .groupby("sprint")["story_points"]
            .sum()
            .mean()
            )

            # Step 4: Filter future sprints and sort by start date
            future_sprints = y_issues[y_issues["sprint_state"] == "Future"]
            future_sprints = future_sprints.sort_values("sprint_start_date")

            # Get next two future sprints
            next_two_future_sprints = future_sprints["sprint"].unique()[:2]

            # Step 5: Calculate total story points for each future sprint
            future_sprint_points = (
            future_sprints[future_sprints["sprint"].isin(next_two_future_sprints)]
            .groupby("sprint")["story_points"]
            .sum()
            )

            # Step 6: Compare future sprint story points with average
            results = []
            for sprint, points in future_sprint_points.items():
            if points >= avg_story_points - 5 and points <= avg_story_points + 5:
                  status = "Okay Utilization"
            elif points < avg_story_points - 5:
                  status = "Underutilized"
            else:
                  status = "Overutilized"
            
            results.append({"Sprint": sprint, "Story Points": points, "Status": status})

            with open("generated_files/output.txt", "w") as f:
                  f.write(f"User Query: Go to previous 2 sprints and calculate the avg story points assigned per sprint and then go to future 2 sprints and check whether its over utilized or underutilized by comparing it to average story points assigned in previous 2 sprints\n\n")
                  f.write("Average Story Points from Last Two Completed Sprints:"+str(avg_story_points))
                  for result in results:
                        f.write("Sprint: "+str(result['Sprint']))
                        f.write("Story Points:"+ str(result['Story Points'])
                        f.write("Status: "+str(result['Status']))
                        f.write("\n")
            #code end
          ''',

    "5":''' specific_need: FTE and FTC ratio for total number of story points in sprint n then
           code for reference: 
            #code start
            import pandas as pd

            # Load the dataset
            df = pd.read_csv("generated_files/output.csv")

            # Filter issues for Sprint n assigned to FTE
            fte_sprintn_issues = df[(df['employee_type'] == 'FTE') & (df['sprint'] == 'Sprint n')]
            total_story_points_fte = fte_sprintn_issues['story_points'].sum()

            # Filter issues for Sprint n assigned to FTC
            ftc_sprintn_issues = df[(df['employee_type'] == 'FTC') & (df['sprint'] == 'Sprint n')]
            total_story_points_ftc = ftc_sprintn_issues['story_points'].sum()

            # Calculate total story points in Sprint n
            total_story_points_sprintn = total_story_points_fte + total_story_points_ftc

            # Calculate percentages for FTE and FTC
            fte_percentage = (total_story_points_fte / total_story_points_sprintn) * 100 if total_story_points_sprintn > 0 else 0
            ftc_percentage = (total_story_points_ftc / total_story_points_sprintn) * 100 if total_story_points_sprintn > 0 else 0

            # Save results to a text file
            with open("generated_files/output.txt", "w") as f:
                  f.write("Total story points assigned to FTE in Sprint n:"+str(total_story_points_fte))
                  f.write("Total story points assigned to FTC in Sprint n:"+str(total_story_points_ftc))
                  f.write("Total story points in Sprint n:"+str(total_story_points_sprintn))
                  f.write("Percentage contribution of FTE:"+str(fte_percentage:.2f)+"%")
                  f.write("Percentage contribution of FTC:"+str(ftc_percentage:.2f)+"%")
                  f.write("FTE to FTC ratio:"+str(total_story_points_fte)+":"+str(total_story_points_ftc))
            #code end
            ''',

    "6":''' specific_need: FTE and FTC ratio for total number of story points assigned to y board in sprint n seperately then 
           code for reference: 
                  #code start
                  import pandas as pd
                  # Load the dataset
                  df = pd.read_csv("generated_files/output.csv")

                  # Filter issues for Sprint n assigned to the y board and FTE
                  fte_y_sprintn_issues = df[(df['employee_type'] == 'FTE') & (df['board'] == 'y') & (df['sprint'] == 'Sprint n')]
                  total_story_points_fte_y= fte_y_sprintn_issues['story_points'].sum()

                  # Filter issues for Sprint n assigned to the y board and FTC
                  ftc_y_sprintn_issues = df[(df['employee_type'] == 'FTC') & (df['board'] == 'y') & (df['sprint'] == 'Sprint n')]
                  total_story_points_ftc_y = ftc_y_sprintn_issues['story_points'].sum()

                  # Calculate total story points assigned to the y board in Sprint n
                  total_story_points_y_sprintn = total_story_points_fte_y + total_story_points_ftc_y

                  # Calculate percentages for FTE and FTC
                  fte_percentage_y = (total_story_points_fte_y / total_story_points_y_sprintn) * 100 if total_story_points_y_sprintn > 0 else 0
                  ftc_percentage_y = (total_story_points_ftc_y / total_story_points_y_sprintn) * 100 if total_story_points_y_sprintn > 0 else 0

                  # Save results to a text file
                  with open("generated_files/output.txt", "w") as f:
                        f.write(f"Total story points assigned to FTE in y board for Sprint n:"+str(total_story_points_fte_y))
                        f.write(f"Total story points assigned to FTC in y board for Sprint n:"+str(total_story_points_ftc_y))
                        f.write(f"Total story points assigned to y board in Sprint n:"+str(total_story_points_y_sprintn))
                        f.write(f"Percentage contribution of FTE in y board for Sprint n:"+str(fte_percentage_y:.2f)+"%")
                        f.write(f"Percentage contribution of FTC in y board for Sprint n:"+str(ftc_percentage_y:.2f)+"%")
                        f.write(f"FTE to FTC ratio in y board for Sprint n:"+str(total_story_points_fte_y)+":"+str(total_story_points_ftc_y))
                  #code end
                  ''',

}