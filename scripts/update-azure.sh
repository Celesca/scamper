#!/bin/bash
# =============================================================================
# SCAMPER - Azure Update Deployment Script
# =============================================================================
# Updates existing Azure Container Apps deployment with new images
# Prerequisites: Run deploy-azure.sh first, or have .azure-deployment.env
# =============================================================================

set -e

# Load deployment configuration
if [ -f ".azure-deployment.env" ]; then
    source .azure-deployment.env
else
    echo "Error: .azure-deployment.env not found. Run deploy-azure.sh first."
    exit 1
fi

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║           SCAMPER - Azure Update Script                          ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"

# Build and push new images
echo -e "\n${YELLOW}[1/4]${NC} Building new Backend image..."
az acr build \
    --registry $ACR_NAME \
    --image scamper-backend:latest \
    --file backend/Dockerfile \
    backend/
echo -e "${GREEN}✓ Backend image updated${NC}"

echo -e "\n${YELLOW}[2/4]${NC} Building new Frontend image..."
az acr build \
    --registry $ACR_NAME \
    --image scamper-frontend:latest \
    --file frontend/Dockerfile \
    frontend/
echo -e "${GREEN}✓ Frontend image updated${NC}"

# Update container apps
echo -e "\n${YELLOW}[3/4]${NC} Updating Backend Container App..."
az containerapp update \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image "${ACR_LOGIN_SERVER}/scamper-backend:latest" \
    --output none
echo -e "${GREEN}✓ Backend updated${NC}"

echo -e "\n${YELLOW}[4/4]${NC} Updating Frontend Container App..."
az containerapp update \
    --name $FRONTEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image "${ACR_LOGIN_SERVER}/scamper-frontend:latest" \
    --output none
echo -e "${GREEN}✓ Frontend updated${NC}"

echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    UPDATE COMPLETE!                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${GREEN}Frontend URL:${NC}  ${FRONTEND_URL}"
echo -e "${GREEN}Backend URL:${NC}   ${BACKEND_URL}"
