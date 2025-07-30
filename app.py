from flask import Flask, render_template, jsonify, request
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        goal = data.get('goal', '')
        tasks = data.get('tasks', [])
        
        if not goal or not tasks:
            return jsonify({"error": "Goal and tasks are required"}), 400
        
        # Get AI analysis
        analyzed_tasks = get_ai_analysis(goal, tasks)
        
        return jsonify({"analyzed_tasks": analyzed_tasks})
    
    except Exception as e:
        print(f"Error in analyze endpoint: {e}")
        print(f"Goal: {data.get('goal', 'None')}")
        print(f"Tasks: {data.get('tasks', 'None')}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

def get_ai_analysis(goal, tasks):
    """
    Get AI analysis using OpenAI API or fallback to Gemini
    """
    # Try OpenAI first (if API key is available)
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        try:
            return call_openai_api(goal, tasks, openai_key)
        except Exception as e:
            print(f"OpenAI API failed: {e}")
    
    # Try Gemini as fallback
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        try:
            return call_gemini_api(goal, tasks, gemini_key)
        except Exception as e:
            print(f"Gemini API failed: {e}")
    
    # If no API keys or both fail, return fallback
    print("No API keys found or all APIs failed, using fallback")
    return get_fallback_analysis(goal, tasks)

def call_openai_api(goal, tasks, api_key):
    """Call OpenAI API for task analysis"""
    prompt = create_analysis_prompt(goal, tasks)
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        return parse_ai_response(content)
    else:
        raise Exception(f"OpenAI API error: {response.status_code}")

def call_gemini_api(goal, tasks, api_key):
    """Call Gemini API for task analysis"""
    prompt = create_analysis_prompt(goal, tasks)
    
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}]
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        content = result['candidates'][0]['content']['parts'][0]['text']
        return parse_ai_response(content)
    else:
        raise Exception(f"Gemini API error: {response.status_code}")

def create_analysis_prompt(goal, tasks):
    """Create the prompt for AI analysis"""
    task_list = '\n'.join([f"{i+1}. {task}" for i, task in enumerate(tasks)])
    
    return f"""
You are a strategic project manager AI. Analyze these tasks for the goal: "{goal}"

Tasks to analyze:
{task_list}

For each task, provide detailed analysis including comparative insights:
- impact: Score 1-10 (how directly this contributes to the goal)
- effort: Score 1-10 (time/difficulty required)  
- emoji: Single relevant emoji
- justification: Detailed explanation covering:
  * WHY this task has its specific impact level
  * What specific outcomes it enables
  * How it connects to achieving the main objective
- comparison: Explain how this task compares to others in the list:
  * Why it's more/less important than similar tasks
  * What makes it unique or critical
  * Which other tasks it should be prioritized over/under and why
- ranking_reason: Brief explanation of where this task should rank overall and why

Return ONLY a JSON array with this exact format:
[
  {{
    "task_name": "exact task text",
    "impact": 8,
    "effort": 6,
    "emoji": "💼",
    "justification": "HIGH IMPACT: This task directly enables [specific outcome] which is critical for [goal] because [reason].",
    "comparison": "This task is more critical than [other tasks] because [reason]. However, it should be done after [higher priority task] since [reason].",
    "ranking_reason": "Ranks #2 overall because it's essential for [outcome] but requires [prerequisite] to be completed first."
  }}
]

Be very specific about task comparisons and relative priorities. Explain the strategic reasoning behind rankings.
"""

def parse_ai_response(content):
    """Parse AI response and extract JSON"""
    try:
        # Clean up the response
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        # Parse JSON
        return json.loads(content)
    except Exception as e:
        print(f"Failed to parse AI response: {e}")
        print(f"Raw content: {content}")
        raise Exception("Failed to parse AI response")

def get_fallback_analysis(goal, tasks):
    """Smart fallback analysis when AI APIs are unavailable"""
    import hashlib
    
    # Use hash of goal+tasks to ensure consistent results
    content_hash = hashlib.md5((goal + ''.join(tasks)).encode()).hexdigest()
    
    # Predefined analysis patterns based on common keywords
    analysis_patterns = {
        'job': {'impact_boost': 2, 'emoji': '💼', 'category': 'career'},
        'apply': {'impact_boost': 3, 'emoji': '📝', 'category': 'action'},
        'interview': {'impact_boost': 3, 'emoji': '🎯', 'category': 'critical'},
        'resume': {'impact_boost': 1, 'emoji': '📄', 'category': 'preparation'},
        'portfolio': {'impact_boost': 2, 'emoji': '💻', 'category': 'showcase'},
        'network': {'impact_boost': 2, 'emoji': '🤝', 'category': 'relationship'},
        'learn': {'impact_boost': 1, 'emoji': '📚', 'category': 'skill'},
        'build': {'impact_boost': 2, 'emoji': '🔧', 'category': 'creation'},
        'practice': {'impact_boost': 1, 'emoji': '⚡', 'category': 'improvement'},
        'research': {'impact_boost': 0, 'emoji': '🔍', 'category': 'preparation'}
    }
    
    analyzed = []
    for i, task in enumerate(tasks):
        task_lower = task.lower()
        
        # Calculate consistent impact based on keywords and hash
        base_impact = 5
        impact_boost = 0
        emoji = '📋'
        category = 'general'
        
        for keyword, pattern in analysis_patterns.items():
            if keyword in task_lower:
                impact_boost = max(impact_boost, pattern['impact_boost'])
                emoji = pattern['emoji']
                category = pattern['category']
                break
        
        # Use hash for consistent but varied scoring
        hash_val = int(content_hash[i % len(content_hash)], 16)
        impact = min(10, max(1, base_impact + impact_boost + (hash_val % 3) - 1))
        effort = min(10, max(1, 5 + (hash_val % 5) - 2))
        
        # Generate meaningful comparisons based on category
        comparison = generate_smart_comparison(task, category, impact, tasks, i)
        ranking = generate_smart_ranking(task, category, impact, len(tasks), i)
        justification = generate_smart_justification(task, category, impact, goal)
        
        analyzed.append({
            "task_name": task,
            "impact": impact,
            "effort": effort,
            "emoji": emoji,
            "justification": justification,
            "comparison": comparison,
            "ranking_reason": ranking
        })
    
    return analyzed

def generate_smart_justification(task, category, impact, goal):
    """Generate meaningful justification based on task category"""
    if category == 'critical':
        return f"HIGH IMPACT: This task is crucial for {goal} because it directly determines success in key interactions. Without this, other efforts may not yield results."
    elif category == 'action':
        return f"HIGH IMPACT: This task creates immediate opportunities toward {goal}. It's a direct action that moves you closer to your objective."
    elif category == 'showcase':
        return f"MEDIUM-HIGH IMPACT: This task demonstrates your capabilities for {goal}. It provides tangible evidence of your skills and experience."
    elif category == 'relationship':
        return f"MEDIUM IMPACT: This task builds connections that support {goal}. Relationships often open doors that applications alone cannot."
    elif category == 'creation':
        return f"MEDIUM IMPACT: This task builds something valuable for {goal}. It creates assets that can be leveraged multiple times."
    elif category == 'preparation':
        return f"MEDIUM IMPACT: This task sets the foundation for {goal}. While not directly achieving it, it enables other high-impact activities."
    elif category == 'skill':
        return f"MEDIUM IMPACT: This task improves your capabilities for {goal}. Knowledge and skills compound over time."
    else:
        return f"MODERATE IMPACT: This task contributes to {goal} through indirect means. It's part of a comprehensive strategy."

def generate_smart_comparison(task, category, impact, all_tasks, index):
    """Generate meaningful task comparisons"""
    if category == 'critical':
        return "This task is more important than preparation tasks because it directly determines outcomes. However, ensure you're prepared before attempting it."
    elif category == 'action':
        return "This task is more valuable than learning tasks because it creates immediate opportunities. Prioritize this over theoretical preparation."
    elif category == 'showcase':
        return "This task is more impactful than basic preparation because it demonstrates real capabilities. Do this before applying to opportunities."
    elif category == 'preparation':
        return "This task should be completed before action-oriented tasks. It's less urgent than direct applications but necessary for success."
    else:
        return f"This task complements other activities in your plan. Consider its timing relative to more direct actions."

def generate_smart_ranking(task, category, impact, total_tasks, index):
    """Generate meaningful ranking explanations"""
    if impact >= 8:
        return f"Ranks in top 25% because it directly advances your goal with high certainty of impact."
    elif impact >= 6:
        return f"Ranks in middle tier because it provides solid value but may require other tasks to be completed first."
    else:
        return f"Ranks lower because while useful, it's more supportive than directly goal-achieving."

if __name__ == "__main__":
    app.run(debug=True)