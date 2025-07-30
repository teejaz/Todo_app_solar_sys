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
    print("=== API KEY DEBUG INFO ===")
    
    # Debug environment loading
    print(f"Current working directory: {os.getcwd()}")
    print(f".env file exists: {os.path.exists('.env')}")
    
    # Try OpenAI first (if API key is available)
    openai_key = os.getenv('OPENAI_API_KEY')
    print(f"OpenAI key found: {'Yes' if openai_key else 'No'}")
    if openai_key:
        print(f"OpenAI key length: {len(openai_key)}")
        print(f"OpenAI key starts with: {openai_key[:10]}...")
        # Remove quotes if present
        openai_key = openai_key.strip("'\"")
        print(f"Trying OpenAI API...")
        try:
            result = call_openai_api(goal, tasks, openai_key)
            print("OpenAI API succeeded!")
            return result
        except Exception as e:
            print(f"OpenAI API failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Try Gemini as fallback
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"Gemini key found: {'Yes' if gemini_key else 'No'}")
    if gemini_key:
        print(f"Gemini key length: {len(gemini_key)}")
        print(f"Gemini key starts with: {gemini_key[:10]}...")
        gemini_key = gemini_key.strip("'\"")
        print(f"Trying Gemini API...")
        try:
            result = call_gemini_api(goal, tasks, gemini_key)
            print("Gemini API succeeded!")
            return result
        except Exception as e:
            print(f"Gemini API failed: {e}")
            import traceback
            traceback.print_exc()
    
    # If no API keys or both fail, return fallback
    print("No API keys found or all APIs failed, using fallback")
    print("=== END DEBUG INFO ===")
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
    
    # Updated Gemini API endpoint and model name
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
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
        print(f"Gemini API Response: {response.text}")
        raise Exception(f"Gemini API error: {response.status_code} - {response.text}")

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
    """Simple fallback when AI APIs are unavailable"""
    import hashlib
    import random
    
    # Use hash of goal+tasks to ensure consistent results
    content_hash = hashlib.md5((goal + ''.join(tasks)).encode()).hexdigest()
    random.seed(content_hash)  # Consistent random based on input
    
    # Simple emoji selection
    emojis = ["📋", "💼", "📚", "🔧", "💡", "�", "🚀c", "⚡", "🎨", "🔍", "📝", "💻", "🌟", "🏆", "🔥"]
    
    analyzed = []
    for i, task in enumerate(tasks):
        # Generate consistent but varied scores
        impact = random.randint(3, 9)
        effort = random.randint(2, 8)
        emoji = emojis[i % len(emojis)]
        
        analyzed.append({
            "task_name": task,
            "impact": impact,
            "effort": effort,
            "emoji": emoji,
            "justification": "⚠️ AI analysis not available. Please add an API key to .env file for detailed insights.",
            "comparison": "⚠️ Task comparison requires AI analysis. Add OPENAI_API_KEY or GEMINI_API_KEY to your .env file.",
            "ranking_reason": "⚠️ Strategic ranking requires AI analysis. Configure an API key for detailed reasoning."
        })
    
    return analyzed

if __name__ == "__main__":
    app.run(debug=True)