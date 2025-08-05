#!/bin/bash

echo "🔧 Installing AWS CLI and SAM CLI for deployment..."

# Install AWS CLI v2
echo "📦 Installing AWS CLI v2..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --update

# Install SAM CLI
echo "📦 Installing SAM CLI..."
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install --update

# Verify installations
echo "✅ Verifying installations..."
aws --version
sam --version

# Clean up
rm -rf awscliv2.zip aws sam-installation aws-sam-cli-linux-x86_64.zip

echo "🎉 AWS tools installed successfully!"
echo "Next step: Run 'aws configure' to set up your credentials"
