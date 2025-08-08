# Stage 1: Build the frontend
FROM node:18-slim as frontend-builder
WORKDIR /app/frontend
COPY src/frontend/package.json src/frontend/package-lock.json ./
RUN npm install
COPY src/frontend/ ./
RUN npm run build

# Stage 2: Build the Python backend
FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the built frontend from the previous stage
COPY --from=frontend-builder /app/frontend/build ./src/frontend/build

# Copy the rest of the application code
COPY . .

# Set permissions and logs
RUN mkdir -p /app/logs && \
    chmod -R a+r /app && \
    chmod +x /app/start-local.sh && \
    find /app -type d -exec chmod a+x {} \;

# Expose ports
EXPOSE 8501
EXPOSE 8000

# Entrypoint script
CMD ["/bin/bash", "./start.sh"]