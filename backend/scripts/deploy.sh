#!/bin/bash
# Deployment Script

echo "================================"
echo "Model Deployment Script"
echo "================================"

# Create deployment directory
DEPLOY_DIR="deployment"
mkdir -p "$DEPLOY_DIR"

# Copy necessary files
echo "Copying model files..."
cp -r models "$DEPLOY_DIR/"
cp -r src "$DEPLOY_DIR/"
cp requirements.txt "$DEPLOY_DIR/"
cp -r config "$DEPLOY_DIR/"

# Create Docker file (if needed)
echo "Creating deployment package..."
cd "$DEPLOY_DIR"
tar -czf ../model_deployment.tar.gz .

cd ..
echo "\nDeployment package created: model_deployment.tar.gz"

echo "\n================================"
echo "Deployment preparation complete!"
echo "================================"
