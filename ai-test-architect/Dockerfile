FROM python:3.12-slim

# Install system basics
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keep alive so VS Code can connect
#CMD ["tail", "-f", "/dev/null"]
CMD ["sleep", "infinity"]
