FROM python:3.8.2-alpine3.11

RUN mkdir -p /collector
WORKDIR /collector
COPY requirements.txt /collector

RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

COPY . /collector

ENTRYPOINT ["python", "-u", "collector.py"]