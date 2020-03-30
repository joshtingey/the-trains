FROM python:3.8.2-alpine3.11

RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt /app

RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

EXPOSE 8000

COPY . /app

ENTRYPOINT ["gunicorn", "-w", "1", "-b", ":8000", "app:server"]