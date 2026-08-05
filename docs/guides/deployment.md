# Deployment Guide

This guide outlines the steps required to deploy the application to production.

## Prerequisites
- Docker and Docker Compose installed.
- Access to the production environment.
- Environment variables configured.

## Steps

1. **Build the image:**
   ```bash
   docker build -t app-image:latest .
   ```

2. **Run the containers:**
   ```bash
   docker-compose up -d
   ```

3. **Verify Deployment:**
   Check the health endpoint to ensure the API is running correctly.
   ```bash
   curl https://api.example.com/v1/health
   ```

## Rollback Procedure
If the deployment fails or issues are detected:
1. Revert to the previous image tag.
2. Restart the containers using the old tag.
