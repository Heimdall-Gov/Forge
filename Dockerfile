FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directories
RUN mkdir -p frameworks templates

# Expose ports
EXPOSE 8000 8501

# Start script
RUN echo '#!/bin/bash\npython app.py &\nstreamlit run ui.py --server.port 8501 --server.address 0.0.0.0' > start.sh
RUN chmod +x start.sh

CMD ["./start.sh"]