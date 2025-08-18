# Stage 1: Build the Python backend
FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1     PYTHONFAULTHANDLER=1     PYTHONPATH=/app     PIP_NO_CACHE_DIR=1     PIP_DISABLE_PIP_VERSION_CHECK=1     DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set permissions and logs
RUN mkdir -p /app/logs &&     chmod -R a+r /app &&     find /app -type d -exec chmod a+x {} \;

# Expose ports
EXPOSE 3000

# Entrypoint script
CMD ["fastapi", "run", "src/chatbot/interfaces/whatsapp/webhook_endpoint.py", "--host", "0.0.0.0", "--port", "3000"]