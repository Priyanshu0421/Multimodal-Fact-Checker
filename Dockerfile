FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies and certificates
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Install PyTorch and other requirements
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    torch==2.7.0 \
    -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Set the default command
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]