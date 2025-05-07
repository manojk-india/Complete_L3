# here is where we store the prompt templates



prompt1="""
<QueryDecompositionInstructions>
<Objective>
Split compound queries containing "and" into individual atomic queries while preserving:
1. Single subject per query
2. Clear board/project associations
3. Respect "respectively" indicators
</Objective>

<Rules>
1. Split on both sides of "and" in subjects (people) and objects (boards)
2. Handle "respectively" by pairing order (first subject with first object)
3. Never combine entities - each gets separate query
4. Preserve exact metric wording ("story points")
</Rules>

<Examples>
Original: "Total story points for Uma and Manoj in CDF board"
Decomposed:
1. Total story points assigned to Uma in CDF board
2. Total story points assigned to Manoj in CDF board

Original: "Story points for Uma and Manoj in CDF and EBSNF boards respectively"
Decomposed:
1. Story points assigned to Uma in CDF board
2. Story points assigned to Manoj in EBSNF board

Original: "Total tasks completed by Alice, Bob and Charlie in Q3"
Decomposed:
1. Total tasks completed by Alice in Q3
2. Total tasks completed by Bob in Q3  
3. Total tasks completed by Charlie in Q3

original: "Jira hygiene for boards under APS "
1. Jira hygiene for boards under APS

original: "FTE/FTC utilization for APS and TES boards"
Decomposed:
1. FTE/FTC utilization for APS board
2. FTE/FTC utilization for TES board

original: "RTB/CTB utilization for APS and TES boards"
Decomposed:
1. RTB/CTB utilization for APS board
2. RTB/CTB utilization for TES board


</Examples>

<OutputFormat>
Return numbered list with exact decomposed queries. 
Include brief explanations in parentheses when splitting multi-board "respectively" cases.
</OutputFormat>

<ValidationCheck>
Before finalizing, verify:
✅ No combined subjects/objects remain
✅ All original entities are accounted for
✅ "Respectively" pairings are preserved
✅ Metrics remain identical across splits
</ValidationCheck>
</QueryDecompositionInstructions>

"""

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
   - Match terms after "board" (e.g., "CDF board" → "CDF")
   - Include known board prefixes (e.g., "EBSNF", "KAN")
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
Query: "Total story points for Uma in CDF board"
Output: {"boards": ["CDF"], "names": ["Uma"], "has_time_period": false}

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
<HierarchyRouter level="L3">
note: No function calling is required here 
<Objective>
Determine if L3 board queries require data aggregation at L1 or L2 based on:
1. Metric/entity type (story points vs features)
2. Explicit hierarchy indicators ("boards under")
3. Operational vs strategic terminology
</Objective>

<DecisionMatrix>
| Trigger Type           | Examples                          | Target Level | Rationale                     |
|------------------------|-----------------------------------|--------------|-------------------------------|
| L1 Metrics             | "story points", "FTE/FTC",        | L1 level     | Granular work tracking        |
|                        | "backlog health", "sprint data"   |              |                               |
| L2 Entities            | "features", "epics",              | L2 level     | Product management scope      |
|                        | "RTB/CTB classification"          |              |                               |
| Hierarchy Expansion    | "boards under", "child boards",   | L1 level     | Requires drilling down        |
|                        | "L1 boards" in query              |              |                               |
| Strategic Terms        | "hygiene", "maturity",            | L2 level     | High-level analysis           |
|                        | "portfolio view"                  |              |                               |
</DecisionMatrix>

<ValidationFlow>
1. Check for explicit hierarchy terms → Set level
2. Match metric/entity type → Set level
3. Confirm with L3-L2-L1 ontology → Final decision
4. Handle conflicts: L1 triggers > L2 triggers
</ValidationFlow>

<Examples>
Query: "JIRA hygiene for transaction processing"
→ {"level": "L2 level", "reason": "Strategic term 'hygiene'"}

Query: "Number of features assigned to transaction processing"
→ {"level": "L2 level", "reason": "L2 entity 'features'"}

Query: "Story points for Uma in transaction processing"
→ {"level": "L1 level", "reason": "L1 metric 'story points'"}

Query: "RTB/CTB of L1 boards under transaction processing"
→ {"level": "L1 level", "reason": "Hierarchy term 'L1 boards under'"}
</Examples>

<OutputSchema>
{
  "level": "L1"|"L2",
  "reason": string,
}
</OutputSchema>
</HierarchyRouter>

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




