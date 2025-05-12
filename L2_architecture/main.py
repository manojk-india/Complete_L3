# imports ...
from L2_architecture.utils import *
from L2_architecture.utils import embed_query

# user query entry point 
def feature_Readiness(query_user):
    def find_board_in_string(board_names, text):
        """
        Returns the first board name found in text, or None if none found.
        """
        for board in board_names:
            if board.lower() in text.lower():
                return board
        return None

    query=find_board_in_string(["DEF2", "DEF1", "DEF3"],query_user)

    # GuardRail
    if not query:
        print("Board Not found.")
        return



    # # JIRA API query here ..rsult json file stored in data/result.json
    get_board_features(query)

    # # convert the aquired json to csv here and stored in data/API.csv
    json_to_csv()

    # # now checking acceptance_crieteria and summary and suggesting better changes and ading those to csv file itself 
    process_evaluations()

    # OKR check in description column
    process_csv_and_check_okr()

    df=pd.read_csv("L2_architecture/data/Final_API.csv")
    num_false = (df['OKR'] == "Not Good").sum()


    # #Now we have to check all missing parameters
    missing_value=count_empty_values("L2_architecture/data/API.csv")

    # # This creates a dashboard with any parameters we give == only concebtrating for missing values
    create_missing_values_dashboard(missing_value)

    # # Now worrying abt the quality of data == OverDue features , not so good Acceptance crieteria , Not so good summaries
    # # overdue Task number returned and csv saved in overdue.csv
    no_of_over_due_features=save_overdue_tasks()

    # # No of features with bad acceptance crieteria and summary
    bad_value=count_separate_issues()
    bad_value["Over_due Features"]=no_of_over_due_features
    bad_value["Poor_OKR's"]=num_false


    # # This creates a dashboard with any parameters we give == concentrating on quality
    create_Bad_values_dashboard(bad_value)

    # Filtering out all the Not-Good features both missing and bad quality of acceptance crieteria == Not-Good-issues
    filter_rows_with_missing_values_or_low_quality_data()


    # not waiting for any actions here..creating acceptance crieteria and summaryb reports 
    create_acceptance_improvement_report()
    create_summary_report()


# function for RTB/CTb case
def RTB_CTB_query(query_user):
    def find_board_in_string(board_names, text):
        """
        Returns the first board name found in text, or None if none found.
        """
        for board in board_names:
            if board.lower() in text.lower():
                return board
        return None

    query=find_board_in_string(["DEF1", "DEF2", "DEF3"],query_user)

    # GuardRail
    if not query:
        print("Board Not found.")



    # # JIRA API query here ..rsult json file stored in data/result.json
    get_board_features(query)

    # # convert the aquired json to csv here and stored in data/API.csv
    json_to_csv()

    # For creating missing value dashboard 
    missing_value=count_empty_values("L2_architecture/data/API.csv")
    create_missing_values_dashboard(missing_value)

    # now py static py script for counting RTB/CTB values and storing in Report/output.txt 
    count_requested_by_percentage()



# Now this is the main entry point 
def L2_entry_point(query_user):
    """
    Main entry point for the L2 architecture.
    """
    # Check if the query is related to feature readiness or RTB/CTB
    value=embed_query(query_user)
    if( value[2] == 2):
        # Feature Readiness
        feature_Readiness(query_user)
    else:
        # RTB/CTB
        RTB_CTB_query(query_user)



