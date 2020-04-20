FROM python:3.8.2-slim-buster

RUN mkdir -p /collector
WORKDIR /collector

COPY ./common/requirements.txt ./common/
COPY ./collector/requirements.txt ./
RUN pip install -r ./common/requirements.txt --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

COPY .env .
COPY ./common/ ./common/
COPY ./collector/* ./

ENTRYPOINT ["python", "collector.py"]
