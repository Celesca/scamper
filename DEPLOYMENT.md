# Scamper - Deployment Guide

Complete guide to deploy Scamper (Thai Brand Guardian) to Azure using Docker containers.

## Quick Start

### Prerequisites
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed
- [Docker](https://docs.docker.com/get-docker/) installed (for local testing)
- Azure subscription with sufficient permissions

### Deploy to Azure (One Command)
```bash
# From project root directory
chmod +x scripts/deploy-azure.sh
./scripts/deploy-azure.sh
```

---

## Table of Contents
1. [Local Development](#local-development)
2. [Azure Container Apps Deployment](#azure-container-apps-deployment)
3. [Manual Azure CLI Deployment](#manual-azure-cli-deployment)
4. [Environment Variables](#environment-variables)
5. [Updating Deployment](#updating-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Local Development

### Using Docker Compose
```bash
# Build and run all services
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Health Check: http://localhost:5000/health

### Backend Only (Development)
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Only (Development)
```bash
cd frontend
npm install
npm run dev
```

---

## Azure Container Apps Deployment

### Automated Deployment Script

The easiest way to deploy is using our script:

```bash
# First time deployment
./scripts/deploy-azure.sh
```

This script will:
1. ✅ Create a Resource Group in Southeast Asia (closest to Thailand)
2. ✅ Create Azure Container Registry
3. ✅ Build and push Docker images
4. ✅ Create Container Apps Environment
5. ✅ Deploy Backend and Frontend apps
6. ✅ Configure networking and environment variables

### Expected Output
```
╔══════════════════════════════════════════════════════════════════╗
║                    DEPLOYMENT COMPLETE!                           ║
╚══════════════════════════════════════════════════════════════════╝

Frontend URL:  https://scamper-frontend.xxx.azurecontainerapps.io
Backend URL:   https://scamper-backend.xxx.azurecontainerapps.io
API Health:    https://scamper-backend.xxx.azurecontainerapps.io/health
```

---

## Manual Azure CLI Deployment

If you prefer manual control:

### Step 1: Login to Azure
```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### Step 2: Create Resources
```bash
# Variables
RESOURCE_GROUP="scamper-rg"
LOCATION="southeastasia"
ACR_NAME="scamperacr$(date +%s)"
ENVIRONMENT="scamper-env"

# Create Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Container Registry
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true
```

### Step 3: Build and Push Images
```bash
# Get ACR credentials
ACR_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

# Build Backend
az acr build \
    --registry $ACR_NAME \
    --image scamper-backend:latest \
    --file backend/Dockerfile \
    backend/

# Build Frontend
az acr build \
    --registry $ACR_NAME \
    --image scamper-frontend:latest \
    --file frontend/Dockerfile \
    frontend/
```

### Step 4: Create Container Apps
```bash
# Create Environment
az containerapp env create \
    --name $ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Get ACR credentials
ACR_USER=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASS=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Deploy Backend
az containerapp create \
    --name scamper-backend \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image "${ACR_SERVER}/scamper-backend:latest" \
    --target-port 5000 \
    --ingress external \
    --registry-server $ACR_SERVER \
    --registry-username $ACR_USER \
    --registry-password $ACR_PASS \
    --cpu 1.0 \
    --memory 2.0Gi \
    --min-replicas 1 \
    --max-replicas 3

# Get Backend URL
BACKEND_URL=$(az containerapp show \
    --name scamper-backend \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" -o tsv)

# Deploy Frontend
az containerapp create \
    --name scamper-frontend \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image "${ACR_SERVER}/scamper-frontend:latest" \
    --target-port 3000 \
    --ingress external \
    --registry-server $ACR_SERVER \
    --registry-username $ACR_USER \
    --registry-password $ACR_PASS \
    --cpu 0.5 \
    --memory 1.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars "NEXT_PUBLIC_API_URL=https://${BACKEND_URL}"
```

---

## Environment Variables

### Backend
| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Set to `production` in production |
| `PYTHONUNBUFFERED` | `1` | Enable real-time logging |

### Frontend
| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:5000` | Backend API URL |
| `NODE_ENV` | `development` | Set to `production` in production |

---

## Updating Deployment

After making code changes:

```bash
# Use the update script
./scripts/update-azure.sh
```

Or manually:
```bash
# Rebuild and push images
az acr build --registry $ACR_NAME --image scamper-backend:latest --file backend/Dockerfile backend/
az acr build --registry $ACR_NAME --image scamper-frontend:latest --file frontend/Dockerfile frontend/

# Update container apps
az containerapp update --name scamper-backend --resource-group $RESOURCE_GROUP --image "${ACR_SERVER}/scamper-backend:latest"
az containerapp update --name scamper-frontend --resource-group $RESOURCE_GROUP --image "${ACR_SERVER}/scamper-frontend:latest"
```

---

## Troubleshooting

### View Container Logs
```bash
# Backend logs
az containerapp logs show \
    --name scamper-backend \
    --resource-group $RESOURCE_GROUP \
    --follow

# Frontend logs
az containerapp logs show \
    --name scamper-frontend \
    --resource-group $RESOURCE_GROUP \
    --follow
```

### Check Container Status
```bash
az containerapp show \
    --name scamper-backend \
    --resource-group $RESOURCE_GROUP \
    --query "properties.runningStatus"
```

### Common Issues

**1. Image Pull Errors**
```bash
# Verify ACR credentials
az acr login --name $ACR_NAME
az acr repository list --name $ACR_NAME
```

**2. Health Check Failures**
- Ensure `/health` endpoint returns 200
- Check memory limits (increase if needed)
- Review application logs

**3. CORS Issues**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Backend should allow the frontend origin

### Delete All Resources
```bash
# WARNING: This deletes everything!
az group delete --name scamper-rg --yes --no-wait
```

---

## Cost Estimation

Azure Container Apps pricing (Southeast Asia):
- **vCPU**: ~$0.000024/second
- **Memory**: ~$0.000003/GB/second

**Estimated Monthly Cost:**
- Backend (1 vCPU, 2GB): ~$50-80/month
- Frontend (0.5 vCPU, 1GB): ~$25-40/month
- Container Registry (Basic): ~$5/month

Total: **~$80-125/month** (varies with usage)

> 💡 **Tip:** Use `--min-replicas 0` for cost savings on non-production environments.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Container Apps                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                  Container Apps Environment              ││
│  │                                                          ││
│  │  ┌─────────────────┐      ┌─────────────────┐          ││
│  │  │   Frontend      │      │    Backend      │          ││
│  │  │   (Next.js)     │ ───▶ │    (Flask)      │          ││
│  │  │   Port 3000     │      │    Port 5000    │          ││
│  │  └─────────────────┘      └─────────────────┘          ││
│  │           │                        │                    ││
│  │           ▼                        ▼                    ││
│  │    HTTPS Ingress            HTTPS Ingress               ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                    Azure Container Registry
                   (Docker Image Storage)
```
