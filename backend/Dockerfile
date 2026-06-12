FROM python:3.11-slim

# Create a non-root user for security
RUN useradd -m -u 1000 user
USER root
RUN mkdir -p /app/vector_stores /app/uploads && chmod -R 777 /app/vector_stores /app/uploads
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
USER user

# Copy requirements from the SAME folder (backend/)
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 --find-links https://download.pytorch.org/whl/cpu torch torchvision
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from the backend folder
COPY --chown=user . .

# HF Port
EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]