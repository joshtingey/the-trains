FROM python:3.8.2-slim-buster

RUN mkdir -p /collector
WORKDIR /collector
COPY requirements.txt /collector

RUN pip install -r requirements.txt --no-cache-dir

COPY . /collector

ENTRYPOINT ["python", "-u", "collector.py"]