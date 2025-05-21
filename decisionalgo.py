import pandas as pd

tasks = pd.read_csv("tasks.csv")
profiles = pd.read_csv("profiles.csv")
histperformances = pd.read_csv("histperformances.csv")

#Meant to help easily associate the budget ranges to an integer value.
budget_map = {
    "$5K - $15K": 10000,
    "$15K - $30K": 25000,
    "$30K - $50K": 40000,
    "$50K - $100K": 75000,
    "$100K - $250K": 175000,
    "$250K+": 300000
}
#Word map because all of the words in agent specialties and 
# --- all of the words in the task descriptors are similar but not the same.
keyword_to_specialty = {
    # Project Types
    "mobile app": "code",
    "web application": "code",
    "e-commerce": "business",
    "ai integration": "ai",
    "data analytics": "data",
    "saas platform": "business",
    "iot solution": "code",
    "ux/ui design": "creative",
    "other/unsure": "business",

    # Target Audience
    "customers": "customer",
    "business": "business",
    "enterprise": "business",
    "retail": "customer",
    "education": "learning",
    "healthcare": "healthcare",
    "financial services": "business",

    # Technologies
    "react": "code",
    "react native": "code",
    "ai/ml": "ai",
    "node.js": "code",
    "aws": "code",
    "google cloud": "code",
    "python": "code",
    "tensorflow": "ai",
    
    # Goals
    "increase revenue": "business",
    "cost reduction": "business",
    "user acquisition": "customer",
    "improve retention": "learning",
    "efficiency gains": "business",
    "market expansion": "business",
    "security enhancement": "security",
    "compliance": "law",
    "other/unsure": "business",
}


#Meant to update profile stats with the historical performance metrics. 
agent_stats = histperformances.groupby("agent_id").agg({
    "outcome_success": "mean",
    "outcome_accuracy": "mean",
    "satisfaction": "mean",
    "total_time": "mean",
    "cost": "mean"
}).reset_index().rename(columns={
    "outcome_success": "avg_success",
    "outcome_accuracy": "avg_accuracy",
    "satisfaction": "avg_satisfaction",
    "total_time": "avg_time",
    "cost": "avg_cost"
})

        #merging profiles with updated stats!
profiles = profiles.merge(agent_stats, on="agent_id", how="left")


#"Deciding an Approach" - This is to decide if the best type of agent to use is AI, Human, or a hybrid of the two.
def decide_approach(task):
    urgency = task["urgency"]
    budget = task["budget"]
    budget_est = budget_map.get(budget, 25000)
    balance = task["human_ai_balance"]

    #I tried to mostly base it off the task's human-AI preference.
    if budget_est < 30000 and urgency >= 4: #small budget and fast time-frame == AI might be the best option 
        return "AI agent"
    elif "AI-first" in balance:
        return "AI agent"
    elif "Human-led" in balance:  
        return "human" 
    elif "Balanced" in balance:
        return "hybrid"
    elif "Expert Recommendation" in balance:
        if urgency >= 4:
            return "AI agent"
        elif budget_est >= 50000 and urgency <= 2: #money and more time == human for best quality
            return "human"
        else:
            return "hybrid"
    else:
        return "AI agent" if urgency >= 3 else "human"

#Meant to turn the strings of key technologies into lists 
def parse_list_string(s):
    if isinstance(s, list):
        return s
    if not isinstance(s, str):
        return []
    s = s.strip("[]")
    if not s:
        return []
    return [item.strip(" '\"") for item in s.split(",")]

for col in ["key_techs", "project_goal"]:
    tasks[col] = tasks[col].apply(parse_list_string)

#tries to match agents specialties to the task's key_techs/goals.
        #utilizes the word map!
def specialty_match(agent, task):
    raw_keywords = task["project_goal"] + [task["project_type"]] + task["key_techs"] + [task["target_audience"]]
    
    normalized_keywords = set()
    for word in raw_keywords:
        if word.lower() in keyword_to_specialty:
            normalized_keywords.add(keyword_to_specialty[word.lower()])
        else:
            normalized_keywords.add(word.lower())

    specialties = set(s.lower() for s in agent.get("specialities", []))
    techs = set(t.lower() for t in agent.get("best_techs", []))

    match_score = sum(1 for kw in normalized_keywords if kw in specialties or kw in techs)

    return match_score / max(len(normalized_keywords), 1)

#Scores each agent based on the task plugged into the function
def scoring_system(agent, task):
    time = agent["avg_completion_min"]
    cost = time * agent["cost_per_min"]
    success = agent.get("avg_success", 0.7)
    accuracy = agent.get("avg_accuracy", 0.7)
    satisfaction = agent.get("avg_satisfaction", 7)
    specialty_score = specialty_match(agent, task)

    score = (
        0.1 * (1 / time) +
        0.15 * accuracy +
        0.1 * success +
        0.15 * (satisfaction / 10) +
        0.4 * specialty_score - 
        0.1 * (cost / budget_map[task["budget"]])
    )
    return score  

agent_task_counts = {agent_id: 0 for agent_id in profiles["agent_id"]}

def get_best_agent(agent_type, task):
    candidates = profiles[profiles["agent_type"] == agent_type]
    if candidates.empty:
        return None

    def penalized_score(agent): #prevents the same agents from being used for every task based off their cost and speed. 
        base_score = scoring_system(agent._asdict(), task)
        penalty = 0.05 * agent_task_counts.get(agent.agent_id, 0)
        return base_score - penalty

    best_agent = max(candidates.itertuples(), key=penalized_score)
    return best_agent

#final function that utilizes scoring function + helper function to assign
def agent_assignment(task):
    approach = decide_approach(task)

    if approach == "hybrid":
        best_ai = get_best_agent("AI agent", task)
        best_human = get_best_agent("human", task)

        lead = (
            "AI agent" if "AI-first" in task["human_ai_balance"] else
            "human" if "Human-led" in task["human_ai_balance"] else
            "hybrid"
        )

        total_time = (best_ai.avg_completion_min + best_human.avg_completion_min) / 2
        total_cost = (
            best_ai.avg_completion_min * best_ai.cost_per_min +
            best_human.avg_completion_min * best_human.cost_per_min
        )

        agent_task_counts[best_ai.agent_id] += 1
        agent_task_counts[best_human.agent_id] += 1

        return {
            "task_id": task["task_id"],
            "approach": "hybrid",
            "assigned_agents": [best_ai.agent_id, best_human.agent_id],
            "agent_types": ["AI agent", "human"],
            "lead_agent_type": lead,
            "expected_total_time": round(total_time, 2),
            "expected_total_cost": round(total_cost, 2)
        }

    else:
        best = get_best_agent(approach, task)
        total_time = best.avg_completion_min
        total_cost = total_time * best.cost_per_min

        agent_task_counts[best.agent_id] += 1

        return {
            "task_id": task["task_id"],
            "approach": approach,
            "assigned_agents": [best.agent_id],
            "agent_types": [approach],
            "lead_agent_type": approach,
            "expected_total_time": round(total_time, 2),
            "expected_total_cost": round(total_cost, 2)
        }

# Apply to all tasks
assignments = [agent_assignment(task) for _, task in tasks.iterrows()]

# Output to JSON or CSV
output_df = pd.DataFrame(assignments)
output_df.to_csv("task_assignments.csv", index=False)
output_df.to_json("task_assignments.json", orient="records", indent=2)

print("Tasks are now assigned.")