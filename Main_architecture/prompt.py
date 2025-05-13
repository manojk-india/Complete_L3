# here is where we store the prompt templates



prompt2="""
<JiraQueryParser>
<Objective>
Extract 3 elements from JIRA queries:
1. Board names (any term following "board" or known board prefixes)
2. Person names (proper nouns likely to be assignees/reporters)
3. Time period indicators (sprints, dates, quarters)

Output format: JSON with keys "boards", "names", "has_time_period"
</Objective>

<ExtractionRules>
1. **Boards**:
   - Match terms after "board" (e.g., "abc1 board" → "abc1")
   - Case-insensitive matching

2. **Names**:
   - Extract capitalized proper nouns not in stopwords
   - Validate against common JIRA user name patterns
   - Handle multi-word names (e.g., "Vanessa Smith")

3. **Time Periods**:
   - Flag for: 
     - Sprint numbers (e.g., "sprint 8")
     - Date ranges ("last week", "Q2")
     - Relative periods ("last 30 days")
     - Fixed dates ("2025-04-21")
</ExtractionRules>

<Examples>
Query: "Total story points for Uma in abc1 board"
Output: {"boards": ["abc1"], "names": ["Uma"], "has_time_period": false}

Query: "Issues assigned to Manoj during sprint 8"
Output: {"boards": [], "names": ["Manoj"], "has_time_period": true}

Query: "Bugs in EBSNF and KAN boards for Alice last quarter"
Output: {"boards": ["EBSNF","KAN"], "names": ["Alice"], "has_time_period": true}
</Examples>

<ValidationSteps>
1. Confirm board names match JIRA board naming conventions
2. Verify names exist in user directory (simulated check)
3. Check time expressions against JQL date formats
</ValidationSteps>

<ErrorHandling>
- Return "None" for absent elements
- Maintain original query casing in output
- Handle multiple entities with array storage
</ErrorHandling>
</JiraQueryParser>

"""

prompt3="""
<QueryGenerator>
<Objective>
Generate specific JIRA queries by combining input parameters (boards, names) with the original query template.  
Output format: List of string queries 
</Objective>

<Rules>
1. **Board Handling**  
   - If original query contains board: Replace with each board from input
   - Else: Append " in board board" for each board

2. **Name Handling**  
   - Always preserve original name placement
   - If multiple names: Create permutations (not needed in current examples)

3. **Parameter Injection**  
   - Maintain original query structure  
   - Preserve non-board/non-name clauses (e.g., "sprint 8")  
   - Use exact board/name casing from inputs
</Rules>

<Examples>
Input:
  Original: "no of story points assigned to Uma in sprint 8"  
  Boards: ["CDF","EBSNF"]  
  Names: ["Uma"]
Output:
{
  "queries": [
    "no of story points assigned to Uma in CDF board in sprint 8",
    "no of story points assigned to Uma in EBSNF board in sprint 8"  
  ]
}

Input:  
  Original: "no of story points assigned to Uma in CDF board"  
  Boards: ["CDF"]  
  Names: ["Uma"]
Output:
{
  "queries": [
    "no of story points assigned to Uma in CDF board"  
  ]
}
</Examples>

<Validation>
1. Query count must equal board count  
2. All board mentions must match input list  
3. Original query semantics preserved  
4. No duplicate queries generated`
</Validation>

</QueryGenerator>
"""

prompt4="""
<HierarchyRouter>
<Objective>
Determine if input query requires L1-level data aggregation based on:
1. Presence of L1-trigger keywords/phrases
2. Existence of hierarchical expansion indicators
3. Specific board reference patterns
</Objective>

<DecisionMatrix>
| Trigger Type           | Examples                          | L1 Required? |
|------------------------|-----------------------------------|--------------|
| Direct L1 Keywords     | "backlog health", "FTE", "FTC",   | Yes          |
|                        | "story points", "boards under"   |              |
| Aggregate Requests     | "all boards", "classification for | Yes          |  
|                        | boards under X"                   |              |
| Specific Board Ref     | "for APS board", "in CDF board"   | No           |
| Ambiguous Indicators   | "summary", "overview", "total"    | Maybe        |
</DecisionMatrix>

<ValidationFlow>
1. Check for exact L1 keywords → If found → L1=True
2. Detect hierarchical terms ("under", "child of") → L1=True  
3. Look for board-specific references without aggregation → L1=False
4. Cross-validate with known L1/L2 criteria → Final decision
</ValidationFlow>

<Examples>
Query: "Backlog health for Q2" 
→ {"value": true, "reason": "Direct L1 keyword 'backlog health'"}

Query: "FTE allocation in EBSNF board"  
→ {"value": true, "reason": "L1 keyword 'FTE' with board context"}

Query: "RTB/CTB classification for APS board" 
→ {"value": false, "reason": "Specific board reference"}

Query: "Boards under APS with high CTB" 
→ {"value": true, "reason": "Hierarchical expansion 'boards under'"}
</Examples>

<OutputFormat>
{
  "value": boolean,
  "reason": "concise justification",
}
</OutputFormat>
</HierarchyRouter>

"""


prompt5="""
Objective:
Determine whether a query about an L3 board requires data aggregation from L1 or L2 based on:

1. The type of metric or entity used (e.g., "story points" vs "features")
2. Presence of explicit hierarchy indicators (e.g., "boards under")
3. Whether the terminology is operational or strategic in nature

Trigger Types and Logic:

L1 Metrics
Examples include: story points, FTE/FTC, backlog health, sprint data
Target Level: L1
Rationale: These are used for granular work tracking

L2 Entities
Examples include: features, epics, RTB/CTB classification, feature hygiene, feature readiness
Target Level: L2
Rationale: These fall under the scope of product management

Hierarchy Expansion
Examples include:child boards, L1 boards
Target Level: L1
Rationale: These require drilling down into the hierarchy

Strategic Terms
Examples include: feature hygiene, maturity, portfolio view
Target Level: L2
Rationale: These terms are typically used in high-level or strategic discussions

Validation Flow:

1. Check for explicit hierarchy terms and set level accordingly
2. Match the metric or entity type and assign a level
3. Confirm the result using the L3-L2-L1 structure
4. In case of conflicting triggers, prioritize L1 triggers over L2 triggers

Examples:

Query: "Feature hygiene for transaction processing"
Result: Level = L2, Reason = L2 entity "feature hygiene"

Query: "Number of features assigned to transaction processing"
Result: Level = L2, Reason = L2 entity "features"

Query: "Story points for Uma in transaction processing"
Result: Level = L1, Reason = L1 metric "story points"

Query: "RTB/CTB of L1 boards under transaction processing"
Result: Level = L1, Reason = Hierarchy term "L1 boards under"

Query: "Feature hygiene for board under GHI board"
Result: Level = L2, Reason = L2 strategic term "feature hygiene"

"""

# DataFrame structure
df_structure = """
The dataset has the following columns:
- "key": issue key
- "board": board id to which the issue has been assigned to
- "summary": summary of issues
- "description": description of issue
- "status": ["To Do", "In Progress", "Done"]
- "assignee": assigned person's name
- "reporter": reporter's name
- "acceptance_criteria": acceptance criteria
- "priority": ["High", "Medium", "Low", "Critical"]
- "issue_type": ["Story", "Bug", "Task","Defect"]
- "created": date of creation for the issue (YYYY-MM-DD)
- "closed": closed date (MM-DD-YYYY) , None if issue is not closed
- "labels": List of label names
- "components": List of component names
- "sprint": sprint name
- "sprint_state": ["Completed", "Active", "Future"]
- "sprint_start_date": sprint start date (MM-DD-YYYY)
- "sprint_end_date": sprint end date (MM-DD-YYYY)
- "story_points": story points (numeric)
- "epic_id": epic id 
- "requested_by": RTB or CTB
- "employee_type": employee type of assignee ( FTE or FTC )
"""

df_structure_members ='''
The dataset has the following columns:
- "name": name of the employee
- "L1_Board":L1 board name to which the employee is part of
- "L2_Board":L2 board name to which the employee is part of
- "L3_Board":L3 board name to which the employee is part of

note: a employee can be part of multiple boards...so he can be in multiple rows
'''

df_structure_pto = '''
The dataset has the following columns:
- "name": name of the employee
- "leave_type": type of leave taken by employee (PTO, Sick Leave, etc)
- "start_date": start date of leave (YYYY-MM-DD)
- "end_date": end date of leave (YYYY-MM-DD)
- "total_days": duration of leave in days
- "sprint": sprint name during which the leave was taken
'''




