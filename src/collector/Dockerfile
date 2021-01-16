FROM python:3.8.6-slim-buster

# Create working directory
WORKDIR /collector

# Install dependencies
COPY src/common/requirements.txt common/
COPY src/collector/requirements.txt ./
RUN pip install -r common/requirements.txt -r requirements.txt --no-cache-dir

# Copy common and app code
COPY src/common/ common/
COPY src/collector/ ./
COPY data/berths.json ./

# Define data collector entrypoint
ENTRYPOINT ["python", "collector.py"]