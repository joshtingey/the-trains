FROM python:3.8.2-slim-buster

# Create working directory
WORKDIR /pytest

# Install dependencies
COPY src/requirements.txt ./
COPY src/common/requirements.txt common/
COPY src/collector/requirements.txt collector/
COPY src/generator/requirements.txt generator/
COPY src/dash/requirements.txt dash/
RUN pip install -r requirements.txt \
    -r common/requirements.txt \
    -r collector/requirements.txt \ 
    -r generator/requirements.txt \
    -r dash/requirements.txt \
    --no-cache-dir

# Copy code
COPY setup.cfg ./
COPY src/common/ common/
COPY src/collector/ collector/
COPY src/generator/ generator/
COPY src/dash/ dash/
COPY tests/ tests/

# Add to PYTHONPATH
ENV PYTHONPATH "${PYTHONPATH}:/pytest"

# Define pytest entrypoint
ENTRYPOINT ["pytest", "--pydocstyle", "--flake8", "--black", "-v", "-W", "ignore::pytest.PytestDeprecationWarning", "."]