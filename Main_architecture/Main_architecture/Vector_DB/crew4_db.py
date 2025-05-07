# here we are creating a database of queries and their corresponding data to query and specific needs in the form of a dictionary.

# After seeing data_to_query and specific_need, we can see that data_to_query is enough to get the required leave data ( can vary )

db3={
    "1":''' data_to_query: All issues assigned to x
            Instruction to follow
            1. Go to PTO.csv and get the leave data for x sprint by sprint
            
            code for reference:
            #code start
            import pandas as pd

            pto_df = pd.read_csv('generated_files/PTO.csv')

            # Query: Total leave days for a specific person (e.g., "Alok")
            query_name = "x"

            # Filter PTO data for the given person
            individual_leaves = pto_df[pto_df['name'] == query_name]

            if individual_leaves.empty:
                print("No leave data found for " + query_name + ".")
            else:
                # Group by sprint and calculate total leave days for each sprint
                sprint_leave_days = individual_leaves.groupby('sprint')['total_days'].sum()

                # Print results
                print("Total leave days opted by " + query_name + " sprint by sprint:")
                for sprint, days in sprint_leave_days.items():
                    print("- " + str(sprint) + ": " + str(days) + " days")

            #code end
        ''',
    "2":''' data_to_query: All issues assigned to x board in Sprint n
            Instruction to follow:
            1. Go to generated_files/PTO.csv and get the members of x board 
            2. For each member, get the leave data for x board in sprint n

            code for reference:
            #code start
            #code end 
            '''

}