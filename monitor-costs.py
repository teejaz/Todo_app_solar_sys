#!/usr/bin/env python3
"""
AWS Cost Monitor for AI Goal Visualizer
Tracks spending and provides cost optimization tips
"""

import boto3
import json
from datetime import datetime, timedelta

def get_current_costs():
    """Get current month's costs for the application"""
    client = boto3.client('ce')  # Cost Explorer
    
    # Get costs for current month
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    
    try:
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        
        print("💰 Current Month AWS Costs:")
        print("=" * 40)
        
        total_cost = 0
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['BlendedCost']['Amount'])
                if cost > 0:
                    print(f"{service}: ${cost:.2f}")
                    total_cost += cost
        
        print(f"\n🎯 Total Cost This Month: ${total_cost:.2f}")
        
        # Cost optimization tips
        print("\n💡 Cost Optimization Tips:")
        if total_cost > 10:
            print("⚠️  Consider switching to t4g.nano EC2 if usage is consistent")
        if total_cost > 5:
            print("⚠️  Review Lambda memory allocation (currently optimized)")
        if total_cost < 1:
            print("✅ Great! You're in the free tier range")
            
    except Exception as e:
        print(f"❌ Error getting costs: {e}")
        print("💡 Make sure you have Cost Explorer permissions")

def get_lambda_metrics():
    """Get Lambda function metrics"""
    client = boto3.client('cloudwatch')
    
    try:
        # Get invocation count for last 7 days
        response = client.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Invocations',
            Dimensions=[
                {
                    'Name': 'FunctionName',
                    'Value': 'ai-goal-visualizer-cheap-AIGoalVisualizerFunction-*'
                }
            ],
            StartTime=datetime.now() - timedelta(days=7),
            EndTime=datetime.now(),
            Period=86400,  # 1 day
            Statistics=['Sum']
        )
        
        total_invocations = sum([point['Sum'] for point in response['Datapoints']])
        print(f"\n📊 Lambda Invocations (Last 7 days): {int(total_invocations)}")
        
        # Estimate costs
        if total_invocations > 1000000:  # 1M free tier limit
            excess = total_invocations - 1000000
            estimated_cost = (excess / 1000000) * 0.20
            print(f"💸 Estimated Lambda cost: ${estimated_cost:.2f}")
        else:
            print("✅ Still in Lambda free tier!")
            
    except Exception as e:
        print(f"❌ Error getting Lambda metrics: {e}")

if __name__ == "__main__":
    print("🔍 AI Goal Visualizer - Cost Monitor")
    print("=" * 50)
    
    get_current_costs()
    get_lambda_metrics()
    
    print("\n🎯 Cheapest Deployment Options:")
    print("1. Lambda + API Gateway: $0-5/month (current setup)")
    print("2. Amplify Hosting: $0-15/month")
    print("3. EC2 t4g.nano: ~$3.50/month")
    print("4. App Runner: ~$7-15/month")
