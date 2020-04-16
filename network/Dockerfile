FROM python:3.8.2-slim-buster

RUN mkdir -p /network
WORKDIR /network
COPY requirements.txt /network

RUN pip install -r requirements.txt --no-cache-dir

COPY . /network

ENTRYPOINT ["python", "-u", "network.py"]