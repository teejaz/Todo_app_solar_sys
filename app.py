from flask import Flask, render_template, jsonify, request
import requests
import json
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class TaskCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(200), nullable=False)
    goal = db.Column(db.String(200), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    impact_score = db.Column(db.Integer)
    effort_score = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_name': self.task_name,
            'goal': self.goal,
            'completed_at': self.completed_at.isoformat(),
            'impact_score': self.impact_score,
            'effort_score': self.effort_score
        }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

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
        openai_key = openai_key.strip("'\"🎯")
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
        gemini_key = gemini_key.strip("'\"🎯")
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
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        return parse_ai_response(content)
    else:
        print(f"OpenAI API Response: {response.text}")
        raise Exception(f"OpenAI API error: {response.status_code}")

def call_gemini_api(goal, tasks, api_key):
    """Call Gemini API for task analysis"""
    prompt = create_analysis_prompt(goal, tasks)
    
    # Updated Gemini API endpoint and model name
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
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
    emojis = ["📋", "💼", "📚", "🔧", "💡", "🎯", "🚀", "⚡", "🎨", "🔍", "📝", "💻", "🌟", "🏆", "🔥"]
    
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

@app.route("/complete-task", methods=["POST"])
def complete_task():
    try:
        data = request.get_json()
        task_name = data.get('task_name')
        goal = data.get('goal')
        impact_score = data.get('impact_score')
        effort_score = data.get('effort_score')
        
        if not task_name or not goal:
            return jsonify({"error": "Task name and goal are required"}), 400
        
        completion = TaskCompletion(
            task_name=task_name,
            goal=goal,
            impact_score=impact_score,
            effort_score=effort_score
        )
        
        db.session.add(completion)
        db.session.commit()
        
        return jsonify({"message": "Task completed successfully", "task": completion.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to complete task: {str(e)}"}), 500

@app.route("/task-stats")
def task_stats():
    try:
        # Get last 365 days of data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        
        completions = TaskCompletion.query.filter(
            TaskCompletion.completed_at >= start_date
        ).all()
        
        # Group by date for contribution graph
        daily_data = {}
        for completion in completions:
            date_key = completion.completed_at.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'date': date_key,
                    'count': 0,
                    'tasks': []
                }
            daily_data[date_key]['count'] += 1
            daily_data[date_key]['tasks'].append({
                'task_name': completion.task_name,
                'goal': completion.goal,
                'impact_score': completion.impact_score
            })
        
        # Calculate statistics
        total_tasks = len(completions)
        unique_days = len(daily_data)
        current_streak = calculate_current_streak()
        longest_streak = calculate_longest_streak()
        
        # Goal breakdown
        goal_stats = {}
        for completion in completions:
            if completion.goal not in goal_stats:
                goal_stats[completion.goal] = 0
            goal_stats[completion.goal] += 1
        
        return jsonify({
            'daily_data': list(daily_data.values()),
            'total_tasks': total_tasks,
            'unique_days': unique_days,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'goal_stats': goal_stats
        })
    
    except Exception as e:
        return jsonify({"error": f"Failed to get stats: {str(e)}"}), 500

def calculate_current_streak():
    """Calculate current streak of consecutive days with tasks"""
    today = datetime.utcnow().date()
    streak = 0
    
    for i in range(365):  # Check up to a year back
        check_date = today - timedelta(days=i)
        count = TaskCompletion.query.filter(
            db.func.date(TaskCompletion.completed_at) == check_date
        ).count()
        
        if count > 0:
            streak += 1
        else:
            break  # Streak broken
    
    return streak

def calculate_longest_streak():
    """Calculate longest streak in the last year"""
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=365)
    
    # Get all dates with tasks
    dates_with_tasks = db.session.query(
        db.func.date(TaskCompletion.completed_at).label('date')
    ).filter(
        TaskCompletion.completed_at >= start_date
    ).distinct().all()
    
    date_set = {d.date for d in dates_with_tasks}
    longest = 0
    current = 0
    
    # Check each day in the range
    current_date = start_date
    while current_date <= end_date:
        if current_date in date_set:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
        current_date += timedelta(days=1)
    
    return longest

def create_sample_data():
    """Create sample tasks and goals for testing"""
    sample_data = [
        # Goal: Learn Python
        {"task_name": "Complete Python basics tutorial", "goal": "Learn Python", "impact_score": 8, "effort_score": 5, "completed_at": datetime.utcnow() - timedelta(days=5)},
        {"task_name": "Build a simple calculator app", "goal": "Learn Python", "impact_score": 7, "effort_score": 6, "completed_at": datetime.utcnow() - timedelta(days=4)},
        {"task_name": "Read Python best practices guide", "goal": "Learn Python", "impact_score": 6, "effort_score": 3, "completed_at": datetime.utcnow() - timedelta(days=3)},
        
        # Goal: Get Fit
        {"task_name": "Morning run - 5km", "goal": "Get Fit", "impact_score": 9, "effort_score": 7, "completed_at": datetime.utcnow() - timedelta(days=2)},
        {"task_name": "Gym workout - upper body", "goal": "Get Fit", "impact_score": 8, "effort_score": 8, "completed_at": datetime.utcnow() - timedelta(days=1)},
        {"task_name": "Yoga session - 30 minutes", "goal": "Get Fit", "impact_score": 7, "effort_score": 4, "completed_at": datetime.utcnow()},
        
        # Goal: Build Portfolio
        {"task_name": "Create personal website homepage", "goal": "Build Portfolio", "impact_score": 9, "effort_score": 6, "completed_at": datetime.utcnow() - timedelta(days=6)},
        {"task_name": "Design project showcase page", "goal": "Build Portfolio", "impact_score": 8, "effort_score": 5, "completed_at": datetime.utcnow() - timedelta(days=5)},
        {"task_name": "Add contact form", "goal": "Build Portfolio", "impact_score": 7, "effort_score": 4, "completed_at": datetime.utcnow() - timedelta(days=4)},
        
        # Goal: Read More Books
        {"task_name": "Read 'Atomic Habits' - Chapter 1-3", "goal": "Read More Books", "impact_score": 6, "effort_score": 5, "completed_at": datetime.utcnow() - timedelta(days=3)},
        {"task_name": "Read 'Deep Work' - Chapter 1-2", "goal": "Read More Books", "impact_score": 7, "effort_score": 5, "completed_at": datetime.utcnow() - timedelta(days=2)},
        {"task_name": "Write book notes for 'Atomic Habits'", "goal": "Read More Books", "impact_score": 5, "effort_score": 3, "completed_at": datetime.utcnow() - timedelta(days=1)},
        
        # Goal: Learn Machine Learning
        {"task_name": "Complete ML basics course module 1", "goal": "Learn Machine Learning", "impact_score": 8, "effort_score": 7, "completed_at": datetime.utcnow() - timedelta(days=7)},
        {"task_name": "Implement linear regression from scratch", "goal": "Learn Machine Learning", "impact_score": 9, "effort_score": 8, "completed_at": datetime.utcnow() - timedelta(days=6)},
        {"task_name": "Study neural networks fundamentals", "goal": "Learn Machine Learning", "impact_score": 8, "effort_score": 6, "completed_at": datetime.utcnow() - timedelta(days=5)},
    ]
    
    # Check if data already exists
    if TaskCompletion.query.first() is None:
        for data in sample_data:
            task = TaskCompletion(
                task_name=data["task_name"],
                goal=data["goal"],
                impact_score=data["impact_score"],
                effort_score=data["effort_score"],
                completed_at=data["completed_at"]
            )
            db.session.add(task)
        
        db.session.commit()
        print(f"Created {len(sample_data)} sample tasks")
    else:
        print("Sample data already exists")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_sample_data()  # Add sample data
    app.run(debug=True, port=5001, host='0.0.0.0')

# Production deployment
if __name__ != "__main__":
    with app.app_context():
        db.create_all()