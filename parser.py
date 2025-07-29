import json

def extract_tasks(raw_text):
    try:
        data = json.loads(raw_text)
        tasks = data.get("tasks", [])
        goal = data.get("goal", "No goal found")
        return tasks, goal
    except json.JSONDecodeError:
        return [], "Invalid JSON format"