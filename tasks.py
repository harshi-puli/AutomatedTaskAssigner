import random
import pandas as pd

#This is the code to generate the three datasets!!
def random_subset(options, min_items=1, max_items=3):
    #This is a function to allow the generator to select multiple items
    return random.sample(options, k=random.randint(min_items, max_items))

#Task Data Generation - the different categories are based off the MOCCET Task options
project_types = ["Mobile App", "Web Application", "E-commerce", "AI Integration", "Data Analytics", "SaaS Platform", "IoT Solution", "UX/UI Design", "Other/unsure"]
target_audience = ["Customers", "Business", "Enterprise", "Retail", "Education", "Healthcare", "Financial Services", "Other/unsure"]
timelines = ["2-4 weeks", "1-2 months", "3-4 months", "5-6 months", "6+ months", "Other/unsure"]
budgets = ["$5K - $15K", "$15K - $30K", "$30K - $50K", "$50K - $100K", "$100K - $250K", "$250K+"]
human_ai_balance = ["Balanced Human + AI", "AI-first Approach", "Human-led with AI Support", "Expert Recommendation", "Other/unsure"]
technologies = ["React", "React Native", "AI/ML", "Node.js", "AWS", "Google Cloud", "Python", "TensorFlow", "Other/unsure"]
org_types = ["Startup", "Enterprise", "Bank/Financial", "Government", "Non-profit", "Other/unsure"]
goals = ["Increase Revenue", "Cost Reduction", "User Acquisition", "Improve Retention", "Efficiency Gains", "Market Expansion", "Security Enhancement", "Compliance", "Other/unsure"]
urgencies = {timelines[i]: 5-i for i in range(len(timelines))}

def generate_synthetic_tasks(n=150):
    tasks = []
    for i in range(n):
        t =  random.choice(timelines)
        task = {
            "task_id": i,
            "urgency": urgencies[t],  #urgency based on timeline.
            "budget": random.choice(budgets),
            "org_type": random.choice(org_types),
            "key_techs": random_subset(technologies),
            "project_goal": random_subset(goals),
            "project_type": random.choice(project_types),
            "target_audience": random.choice(target_audience),
            "timeline": t,
            "human_ai_balance": random.choice(human_ai_balance)
        }
        tasks.append(task)
    return tasks


synthetic_data = generate_synthetic_tasks()

df = pd.DataFrame(synthetic_data)

print("Synthetic Tasks Generated")

df.to_csv('tasks.csv', index=False)


#Agent Profiles Dataset Generation
agent_types = ["human", "AI agent"]
specialties = ["business", "law", "healthcare", "security", "creative", "learning", "code", "data", "customer"]
best_techs = ["React", "React Native", "AI/ML", "Node.js", "AWS", "Google Cloud", "Python", "TensorFlow", "Other/unsure"]

def generate_synthetic_profiles(n=20):
    profiles = []

    #To keep things simple, I made it so that IDs are equal to their profile's index.
    for id in range(n):
        a = random.choice(agent_types)

        #giving human agents slow
        if a == "human":
            avg_time = random.randint(30, 70) 
            cpm = random.uniform(0.1, 0.5)
        else:
            avg_time = random.randint(60, 120) 
            cpm = random.uniform(0.75, 2.0)

        profile = {
            "agent_id": id,
            "agent_type": a,
            "efficiency": round(random.uniform(0.6, 1.0) if a == "AI agent" else random.uniform(0.4, 0.9),2),
            "cost_per_min": round(cpm,2),
            "specialities": random_subset(specialties, 1, 5) if a == "human" else random_subset(specialties),
            "learning_rate": random.uniform(0.1, 0.5) if a == "human" else random.uniform(0.6, 0.9),
            "avg_completion_min": avg_time,
            "best_techs": random_subset(technologies)
        }
        profiles.append(profile)
    return profiles

synthetic_profiles = generate_synthetic_profiles(20)

pdf = pd.DataFrame(synthetic_profiles)

print("Synthetic Profiles Generated")

pdf.to_csv('profiles.csv', index=False)


#Historical Performance data generation
def generate_synthetic_performances(n=500):
    performances = []

    for i in range(n):
        agent = random.randint(0,19)
        accuracy = random.uniform(0.1, 0.7) if synthetic_profiles[agent]["agent_type"] == "AI agent" else random.uniform(0.4, 0.9)
        success_prob = accuracy * 0.8 + 0.1
        success = random.uniform(0.1,0.9) < success_prob
        avg_time = synthetic_profiles[agent]["avg_completion_min"]
        t = round(max(30,min(150,random.gauss(avg_time, avg_time * 0.1),2)))

        performance = {
            "task_id": 700-i,
            "agent_id": agent,
            "outcome_success": success,
            "outcome_accuracy": accuracy,
            "total_time": t,
            "cost": round(t * synthetic_profiles[agent]["cost_per_min"], 2),
            "satisfaction": random.randint(6,10) if success else random.randint(1,5)
        }
        performances.append(performance)
    return performances


synthetic_performances = generate_synthetic_performances()

hp = pd.DataFrame(synthetic_performances)

print("Synthetic Historical Performances Generated")

hp.to_csv('histperformances.csv', index=False)