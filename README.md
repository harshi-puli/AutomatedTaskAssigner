This is my algorithm for assigning particular tasks to a set of AI and human agents.

I worked with 3 datasets: 
1. Tasks (150) - task ID, key techs, project goal, urgency, etc.
2. Profiles (20) - agent ID, AI or Human, best techs, avg completion time (minutes),  
3. Historical Performance Metrics (500) - task ID,

The task allocation process:
1. User human/AI agent preference
2. Does the budget and time allow for the preference to work?
3. Scoring each agents potential for a task based on shared characteristics + penalization to their score when agents are assigned to too many
4. Choosing the best score out of all AI/human/hybrid agent(s) and assigning them the task!
