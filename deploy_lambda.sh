#!/bin/bash
set -e

# Prepare Lambda deployment package with correct structure
rm -rf deployment lambda-deployment.zip
mkdir -p deployment/templates
cp templates/index.html deployment/templates/
cp lambda_function.py deployment/

cd deployment
zip -r ../lambda-deployment.zip .
cd ..
rm -rf deployment

echo "Uploading to Lambda..."
aws lambda update-function-code \
  --function-name ai-goal-visualizer-cheap-AIGoalVisualizerFunction-1fbqiNiNIqH3 \
  --zip-file fileb://lambda-deployment.zip \
  --region us-east-1

echo "Cleaning up..."
rm -f lambda-deployment.zip

echo "Deployment complete."
