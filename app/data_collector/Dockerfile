FROM python:3.8.2-slim-buster

RUN mkdir -p /data_collector
WORKDIR /data_collector

COPY ./app/common/requirements.txt ./common/
COPY ./app/data_collector/requirements.txt ./
RUN pip install -r ./common/requirements.txt --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

COPY .env .
COPY ./app/common/ ./common/
COPY ./app/data_collector/* ./
COPY ./app/data_collector/data/* ./data/

ENTRYPOINT ["python", "data_collector.py"]