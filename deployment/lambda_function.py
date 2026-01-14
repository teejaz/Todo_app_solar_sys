import json
import boto3
import os
from datetime import datetime, timedelta
from urllib.parse import parse_qs

# Simple in-memory storage for Lambda (replace with DynamoDB for production)
task_storage = []

def lambda_handler(event, context):
    """Main Lambda handler for goal visualization app"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle OPTIONS for CORS
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Route handling
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    if path == '/' or path == '':
        return serve_index()
    elif path == '/analyze' and method == 'POST':
        return analyze_tasks(event)
    elif path == '/complete-task' and method == 'POST':
        return complete_task(event)
    elif path == '/task-stats':
        return get_task_stats()
    else:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Not found'})
        }

def serve_index():
    """Serve the main index page with integrated dashboard"""
    try:
        with open('templates/index.html', 'r') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': html_content
        }
    except FileNotFoundError:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Index template not found'})
        }

def analyze_tasks(event):
    """Analyze tasks and return visualization data"""
    try:
        body = json.loads(event.get('body', '{}'))
        goal = body.get('goal', '')
        tasks_text = body.get('tasks', '')
        
        if not goal or not tasks_text:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Goal and tasks are required'})
            }
        
        # Parse tasks
        tasks = [task.strip() for task in tasks_text.split('\n') if task.strip()]
        
        # Mock analysis (replace with actual AI logic)
        analyzed_tasks = []
        for i, task in enumerate(tasks):
            analyzed_tasks.append({
                'task_name': task,
                'impact': 7 + (i % 4),  # Mock impact score
                'effort': 3 + (i % 5),  # Mock effort score
                'emoji': '🎯',
                'justification': f'This task helps achieve your goal of {goal}',
                'priority': 'High' if i < 2 else 'Medium',
                'comparison': 'This task has higher impact than similar tasks',
                'ranking_reason': f'Ranked #{i+1} based on impact-effort analysis'
            })
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'tasks': analyzed_tasks})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Analysis failed: {str(e)}'})
        }

def complete_task(event):
    """Mark a task as complete"""
    try:
        body = json.loads(event.get('body', '{}'))
        task_name = body.get('task_name', '')
        goal = body.get('goal', '')
        impact_score = body.get('impact_score', 0)
        effort_score = body.get('effort_score', 0)
        
        if not task_name or not goal:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Task name and goal are required'})
            }
        
        # Store task completion
        completion = {
            'id': len(task_storage) + 1,
            'task_name': task_name,
            'goal': goal,
            'completed_at': datetime.utcnow().isoformat(),
            'impact_score': impact_score,
            'effort_score': effort_score
        }
        task_storage.append(completion)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Task completed successfully', 'task': completion})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Failed to complete task: {str(e)}'})
        }

def get_task_stats():
    """Get task completion statistics"""
    try:
        # Mock data for dashboard (replace with real data from task_storage)
        daily_data = [
            {
                'date': '2026-01-10',
                'count': 3,
                'tasks': [
                    {'task_name': 'Complete project setup', 'goal': 'Learn AWS', 'impact_score': 8},
                    {'task_name': 'Deploy dashboard', 'goal': 'Learn AWS', 'impact_score': 7}
                ]
            },
            {
                'date': '2026-01-11',
                'count': 2,
                'tasks': [
                    {'task_name': 'Fix hover effects', 'goal': 'Improve UI', 'impact_score': 6}
                ]
            }
        ]
        
        # Calculate statistics
        total_tasks = len(task_storage)
        unique_days = len(set(task['completed_at'][:10] for task in task_storage))
        
        goal_stats = {}
        for task in task_storage:
            if task['goal'] not in goal_stats:
                goal_stats[task['goal']] = 0
            goal_stats[task['goal']] += 1
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'daily_data': daily_data,
                'total_tasks': total_tasks,
                'unique_days': unique_days,
                'current_streak': 3,
                'longest_streak': 5,
                'goal_stats': goal_stats
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Failed to get stats: {str(e)}'})
        }
