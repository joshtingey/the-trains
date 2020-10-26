FROM python:3.8.6-slim-buster

# Create working directory
WORKDIR /dash

# Install dependencies
COPY common/requirements.txt common/
COPY dash/requirements.txt ./
RUN pip install -r ./common/requirements.txt -r requirements.txt --no-cache-dir

# Copy common and dash code
COPY common/ common/
COPY dash/ ./

# Expose the dash app port
EXPOSE 8000

# Define thetrains dash app entrypoint
ENTRYPOINT ["gunicorn", "-w", "4", "-b", ":8000", "index:server"]