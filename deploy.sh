#!/bin/bash
# =============================================================================
# SCAMPER - Azure Container Apps Deployment Script (Simplified)
# =============================================================================
# This script automates the manual deployment steps from DEPLOYMENT.md
# =============================================================================

set -e

# --- Configuration ---
RESOURCE_GROUP="scamper-rg"
LOCATION="southeastasia"
ACR_NAME="scamperacr$(date +%s)"
ENVIRONMENT="scamper-env"
BACKEND_IMAGE="scamper-backend:latest"
FRONTEND_IMAGE="scamper-frontend:latest"

echo "🚀 Starting Scamper Deployment to Azure..."

# Step 1: Login to Azure
echo "🔑 Checking Azure login..."
if ! az account show &>/dev/null; then
    echo "Please login to Azure:"
    az login
fi

# Step 2: Create Resource Group
echo "📁 Creating Resource Group: $RESOURCE_GROUP..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Step 3: Create Container Registry
echo "📦 Creating Azure Container Registry: $ACR_NAME..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR credentials
ACR_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
ACR_USER=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASS=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Step 4: Build and Push Images
echo "🏗️ Building and pushing Backend image..."
az acr build \
    --registry $ACR_NAME \
    --image $BACKEND_IMAGE \
    --file backend/Dockerfile \
    backend/

echo "🏗️ Building and pushing Frontend image..."
az acr build \
    --registry $ACR_NAME \
    --image $FRONTEND_IMAGE \
    --file frontend/Dockerfile \
    frontend/

# Step 5: Create Container Apps Environment
echo "🌐 Creating Container Apps Environment: $ENVIRONMENT..."
az containerapp env create \
    --name $ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Step 6: Deploy Backend Container App
echo "🚀 Deploying Backend Container App..."
az containerapp create \
    --name scamper-backend \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image "${ACR_SERVER}/${BACKEND_IMAGE}" \
    --target-port 5000 \
    --ingress external \
    --registry-server $ACR_SERVER \
    --registry-username $ACR_USER \
    --registry-password $ACR_PASS \
    --cpu 1.0 \
    --memory 2.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars "FLASK_ENV=production"

# Get Backend URL
BACKEND_URL=$(az containerapp show \
    --name scamper-backend \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" -o tsv)

echo "✅ Backend deployed at: https://${BACKEND_URL}"

# Step 7: Deploy Frontend Container App
echo "🚀 Deploying Frontend Container App..."
az containerapp create \
    --name scamper-frontend \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image "${ACR_SERVER}/${FRONTEND_IMAGE}" \
    --target-port 3000 \
    --ingress external \
    --registry-server $ACR_SERVER \
    --registry-username $ACR_USER \
    --registry-password $ACR_PASS \
    --cpu 0.5 \
    --memory 1.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars "NEXT_PUBLIC_API_URL=https://${BACKEND_URL}" "NODE_ENV=production"

# Get Frontend URL
FRONTEND_URL=$(az containerapp show \
    --name scamper-frontend \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" -o tsv)

echo "🎉 DEPLOYMENT COMPLETE!"
echo "--------------------------------------------------"
echo "Frontend URL:  https://${FRONTEND_URL}"
echo "Backend URL:   https://${BACKEND_URL}"
echo "--------------------------------------------------"
