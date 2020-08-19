FROM python:3.8.2-slim-buster

# Create working directory
WORKDIR /generator

# Install dependencies
COPY common/requirements.txt common/
COPY generator/requirements.txt ./
RUN pip install -r ./common/requirements.txt -r requirements.txt --no-cache-dir

# Copy common and app code
COPY common/ common/
COPY generator/ ./

# Define graph generator entrypoint
ENTRYPOINT ["python", "generator.py"]