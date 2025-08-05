#!/bin/bash

echo "🚀 Deploying AI Goal Visualizer without SAM CLI..."

# Set variables
STACK_NAME="ai-goal-visualizer-cheap"
REGION="us-east-1"
BUCKET_NAME="ai-goal-visualizer-deploy-$(date +%s)"

# Create S3 bucket for deployment
echo "📦 Creating S3 bucket for deployment..."
aws s3 mb s3://$BUCKET_NAME --region $REGION

# Create deployment package
echo "📦 Creating deployment package..."
zip -r deployment.zip . -x "*.git*" "*.zip" "venv/*" "__pycache__/*" "*.pyc"

# Upload to S3
echo "⬆️ Uploading deployment package..."
aws s3 cp deployment.zip s3://$BUCKET_NAME/deployment.zip

# Create CloudFormation template with S3 reference
cat > template-direct.yaml << EOF
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  AIGoalVisualizerFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: s3://$BUCKET_NAME/deployment.zip
      Handler: lambda_function.lambda_handler
      Runtime: python3.11
      MemorySize: 256
      Timeout: 15
      Environment:
        Variables:
          OPENAI_API_KEY: dummy
          GEMINI_API_KEY: dummy
      Events:
        CatchAll:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
        Root:
          Type: Api
          Properties:
            Path: /
            Method: ANY

Outputs:
  ApiUrl:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://\${ServerlessRestApi}.execute-api.\${AWS::Region}.amazonaws.com/Prod/"
EOF

# Deploy using CloudFormation
echo "🚀 Deploying CloudFormation stack..."
aws cloudformation deploy \
  --template-file template-direct.yaml \
  --stack-name $STACK_NAME \
  --capabilities CAPABILITY_IAM \
  --region $REGION

# Get the API URL
echo "🎉 Deployment complete!"
API_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text \
  --region $REGION)

echo "🌍 Your AI Goal Visualizer is live at: $API_URL"
echo "💰 Expected monthly cost: $0-5 (first 1M requests free)"

# Clean up
rm deployment.zip template-direct.yaml
echo "🧹 Cleaned up temporary files"
