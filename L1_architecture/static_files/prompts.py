# here is where prompt templates are written 


df_structure_main="""
The csv file has the following columns:
- "key": issue key (string)
- "project_key": board name (string)
- "summary": summary of issues (string)
- "description": description of issue (string)
- "status": one of ["To Do", "In Progress", "Done"]
- "assignee": assigned person's name (string)
- "reporter": reporter's name (string)
- "acceptance_criteria": acceptance criteria (string)
- "priority": one of ["High", "Medium", "Low", "Critical"]
- "issue_type": one of ["Story", "Bug", "Task", "Defect"]
- "labels": list of label names (list of strings)
- "components": list of component names (list of strings)
- "sprint": sprint name (string)
- "sprint_state": one of ["Completed", "Active", "Future"]
- "story_points": story points (numeric)
- "requested_by": either "RTB" or "CTB"
- "employee_type": employee type of assignee (either "FTE" or "FTC")"""