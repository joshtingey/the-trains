FROM python:3.8.6-slim-buster

# Create working directory
WORKDIR /generator

# Install dependencies
COPY src/common/requirements.txt common/
COPY src/generator/requirements.txt ./
RUN pip install -r ./common/requirements.txt -r requirements.txt --no-cache-dir

# Copy common and app code
COPY src/common/ common/
COPY src/generator/ ./

# Define graph generator entrypoint
ENTRYPOINT ["python", "generator.py"]