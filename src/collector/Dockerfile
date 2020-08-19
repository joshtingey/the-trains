FROM python:3.8.2-slim-buster

# Create working directory
WORKDIR /collector

# Install dependencies
COPY common/requirements.txt common/
COPY collector/requirements.txt ./
RUN pip install -r common/requirements.txt -r requirements.txt --no-cache-dir

# Copy common and app code
COPY common/ common/
COPY collector/ ./

# Define data collector entrypoint
ENTRYPOINT ["python", "collector.py"]