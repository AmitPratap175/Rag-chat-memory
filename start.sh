#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define the port for the backend, defaulting to 8000 if not set
BACKEND_PORT=${PORT:-8000}

echo "Starting production server..."

# Step 1: Build the frontend static files
echo "Building frontend..."
(cd src/frontend && npm install && npm run build) || {
  echo "Frontend build failed. Please check the logs for errors."
  exit 1
}
echo "Frontend build complete."

# Step 2: Start the backend server using uvicorn
echo "Starting backend on port $BACKEND_PORT..."
exec uvicorn src.server:app --host 0.0.0.0 --port "$BACKEND_PORT"
