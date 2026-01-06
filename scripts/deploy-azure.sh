#!/bin/bash
# =============================================================================
# SCAMPER - Azure Container Apps Deployment Script
# =============================================================================
# This script deploys the Scamper application to Azure Container Apps
# Prerequisites: Azure CLI, Docker (optional for local builds)
# =============================================================================

set -e  # Exit on any error

# =============================================================================
# CONFIGURATION - Modify these values as needed
# =============================================================================
RESOURCE_GROUP="scamper-rg"
LOCATION="southeastasia"  # Closest to Thailand
ACR_NAME="scamperacr$(openssl rand -hex 4)"  # Unique ACR name
ENVIRONMENT_NAME="scamper-env"
BACKEND_APP_NAME="scamper-backend"
FRONTEND_APP_NAME="scamper-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║           SCAMPER - Azure Deployment Script                       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"

# =============================================================================
# STEP 1: Login to Azure
# =============================================================================
echo -e "\n${YELLOW}[Step 1/8]${NC} Checking Azure login status..."
if ! az account show &>/dev/null; then
    echo -e "${YELLOW}Not logged in. Please login to Azure...${NC}"
    az login
fi
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo -e "${GREEN}✓ Logged in to Azure (Subscription: $SUBSCRIPTION_ID)${NC}"

# =============================================================================
# STEP 2: Create Resource Group
# =============================================================================
echo -e "\n${YELLOW}[Step 2/8]${NC} Creating Resource Group: ${RESOURCE_GROUP}..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output none
echo -e "${GREEN}✓ Resource Group created${NC}"

# =============================================================================
# STEP 3: Create Azure Container Registry
# =============================================================================
echo -e "\n${YELLOW}[Step 3/8]${NC} Creating Azure Container Registry: ${ACR_NAME}..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --output none
echo -e "${GREEN}✓ Container Registry created${NC}"

# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

echo -e "${CYAN}  ACR Login Server: $ACR_LOGIN_SERVER${NC}"

# =============================================================================
# STEP 4: Build and Push Backend Image
# =============================================================================
echo -e "\n${YELLOW}[Step 4/8]${NC} Building and pushing Backend Docker image..."
az acr build \
    --registry $ACR_NAME \
    --image scamper-backend:latest \
    --file backend/Dockerfile \
    backend/
echo -e "${GREEN}✓ Backend image pushed to ACR${NC}"

# =============================================================================
# STEP 5: Build and Push Frontend Image
# =============================================================================
echo -e "\n${YELLOW}[Step 5/8]${NC} Building and pushing Frontend Docker image..."
az acr build \
    --registry $ACR_NAME \
    --image scamper-frontend:latest \
    --file frontend/Dockerfile \
    frontend/
echo -e "${GREEN}✓ Frontend image pushed to ACR${NC}"

# =============================================================================
# STEP 6: Create Container Apps Environment
# =============================================================================
echo -e "\n${YELLOW}[Step 6/8]${NC} Creating Container Apps Environment: ${ENVIRONMENT_NAME}..."
az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output none
echo -e "${GREEN}✓ Container Apps Environment created${NC}"

# =============================================================================
# STEP 7: Deploy Backend Container App
# =============================================================================
echo -e "\n${YELLOW}[Step 7/8]${NC} Deploying Backend Container App: ${BACKEND_APP_NAME}..."
az containerapp create \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image "${ACR_LOGIN_SERVER}/scamper-backend:latest" \
    --target-port 5000 \
    --ingress external \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --cpu 1.0 \
    --memory 2.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars "FLASK_ENV=production" \
    --output none

BACKEND_URL=$(az containerapp show \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" -o tsv)
echo -e "${GREEN}✓ Backend deployed: https://${BACKEND_URL}${NC}"

# =============================================================================
# STEP 8: Deploy Frontend Container App
# =============================================================================
echo -e "\n${YELLOW}[Step 8/8]${NC} Deploying Frontend Container App: ${FRONTEND_APP_NAME}..."
az containerapp create \
    --name $FRONTEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image "${ACR_LOGIN_SERVER}/scamper-frontend:latest" \
    --target-port 3000 \
    --ingress external \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --cpu 0.5 \
    --memory 1.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars "NEXT_PUBLIC_API_URL=https://${BACKEND_URL}" "NODE_ENV=production" \
    --output none

FRONTEND_URL=$(az containerapp show \
    --name $FRONTEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" -o tsv)
echo -e "${GREEN}✓ Frontend deployed: https://${FRONTEND_URL}${NC}"

# =============================================================================
# DEPLOYMENT COMPLETE
# =============================================================================
echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    DEPLOYMENT COMPLETE!                           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${GREEN}Frontend URL:${NC}  https://${FRONTEND_URL}"
echo -e "${GREEN}Backend URL:${NC}   https://${BACKEND_URL}"
echo -e "${GREEN}API Health:${NC}    https://${BACKEND_URL}/health"
echo -e ""
echo -e "${YELLOW}Resource Group:${NC} ${RESOURCE_GROUP}"
echo -e "${YELLOW}ACR Name:${NC}       ${ACR_NAME}"
echo -e ""
echo -e "${CYAN}To update the deployment later, run:${NC}"
echo -e "  ./scripts/update-azure.sh"
echo -e ""
echo -e "${CYAN}To delete all resources:${NC}"
echo -e "  az group delete --name ${RESOURCE_GROUP} --yes"
echo -e ""

# Save deployment info
cat > .azure-deployment.env << EOF
RESOURCE_GROUP=${RESOURCE_GROUP}
ACR_NAME=${ACR_NAME}
ACR_LOGIN_SERVER=${ACR_LOGIN_SERVER}
ENVIRONMENT_NAME=${ENVIRONMENT_NAME}
BACKEND_APP_NAME=${BACKEND_APP_NAME}
FRONTEND_APP_NAME=${FRONTEND_APP_NAME}
BACKEND_URL=https://${BACKEND_URL}
FRONTEND_URL=https://${FRONTEND_URL}
EOF
echo -e "${GREEN}✓ Deployment info saved to .azure-deployment.env${NC}"
