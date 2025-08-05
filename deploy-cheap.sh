#!/bin/bash

# Cost-Optimized AWS Deployment Script for AI Goal Visualizer

echo "🚀 Deploying AI Goal Visualizer with cost optimization..."

# 1. Build and deploy with SAM (Serverless - cheapest option)
echo "📦 Building SAM application..."
sam build --use-container

echo "🌐 Deploying to AWS Lambda + API Gateway..."
sam deploy \
  --stack-name ai-goal-visualizer-cheap \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    OpenAIApiKey="${OPENAI_API_KEY:-dummy}" \
    GeminiApiKey="${GEMINI_API_KEY:-dummy}" \
  --region us-east-1

echo "✅ Deployment complete!"
echo "💰 Expected monthly cost: $0-5 (only pay for actual usage)"
echo "📊 Monitor costs at: https://console.aws.amazon.com/billing/"

# Get the API endpoint
ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ai-goal-visualizer-cheap \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

echo "🌍 Your app is live at: $ENDPOINT"
