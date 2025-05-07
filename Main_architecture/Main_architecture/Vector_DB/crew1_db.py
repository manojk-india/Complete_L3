# here we are creating a database of queries and their corresponding data to query and specific needs in the form of a dictionary.

db1={
    "1":'''user_query:Sum of all story points assigned to x then
            data_to_query: All issues assigned to x
            specific_need: Sum of all story points assigned to x''',

    "2":''' user_query: Total number story points assigned to RTB , CTB seperately in Sprint n then
            data_to_query: All issues in Sprint n
            specific_need: Total number story points assigned to RTB , CTB seperately in Sprint n''',

    "3":''' user_query: Total number of story points assigned to a and b in sprint n seperately then
            data_to_query: All issues assigned to a and b in sprint n
            specific_need: Story points assigned to a and b seperately in sprint n''',

    "4":''' user_query: All the issues assigned to x in sprint n then
            data_to_query: All issues assigned to x in sprint n
            specific_need: None''',

    "5":''' user_query: How is backlog health looking for y board
            data_to_query: All issues in y board
            specific_need: Calculate the average story points from the last 2 completed sprints in the y board, 
            then compare the total story points of the next 2 future sprints (one at a time) with this average, 
            and classify each future sprint as 'Underutilized', 'Okay Utilization +- 5 from average story points calculated', or 'Overutilized''',

    "6":''' user_query: FTE and FTC ratio for total number of story points in sprint n then
            data_to_query: All issues in sprint n
            specific_need: FTE and FTC ratio for total number of story points in sprint n''',

    "7":''' user_query: FTE and FTC ratio for total number of story points assigned to y board in sprint n
            data_to_query: All issues assigned to y board in sprint n
            specific_need: FTE and FTC ratio for total number of story points assigned to y board in sprint n seperately''',
}