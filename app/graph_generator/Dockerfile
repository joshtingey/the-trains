FROM python:3.8.2-slim-buster

RUN mkdir -p /graph_generator
WORKDIR /graph_generator

COPY ./app/common/requirements.txt ./common/
COPY ./app/graph_generator/requirements.txt ./
RUN pip install -r ./common/requirements.txt --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

COPY .env .
COPY ./app/common/ ./common/
COPY ./app/graph_generator/* ./

ENTRYPOINT ["python", "graph_generator.py"]