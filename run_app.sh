#!/usr/bin/env bash
# Builds and starts the SuperKart backend (Flask) and frontend (Streamlit) containers
set -e

# 1. Create a Docker network so the two containers can talk to each other by name
docker network create superkart-net 2>/dev/null || true

# 2. Remove old containers if this script is run again
docker rm -f backend frontend 2>/dev/null || true

# 3. Build and start the backend (Flask API on port 7860)
docker build -t superkart-backend ./backend
docker run -d --name backend --network superkart-net -p 7860:7860 superkart-backend

# 4. Build and start the frontend (Streamlit UI on port 8501)
docker build -t superkart-frontend ./frontend
docker run -d --name frontend --network superkart-net -p 8501:8501 -e BACKEND_URL=http://backend:7860 superkart-frontend

docker ps
echo "Backend  -> port 7860   |   Frontend -> port 8501"
