FROM python:3.11-slim

# Create a user to avoid permission issues
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install system dependencies (Root required for apt-get)
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
USER user

# Copy requirements from BACKEND folder and install
COPY --chown=user backend/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 --find-links https://download.pytorch.org/whl/cpu torch torchvision
RUN pip install --no-cache-dir -r requirements.txt

# Copy EVERYTHING from backend folder to the container's /app
COPY --chown=user backend/ .

# HF Port
EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]