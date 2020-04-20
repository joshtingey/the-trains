FROM python:3.8.2-slim-buster

RUN mkdir -p /dash
WORKDIR /dash

COPY ./common/requirements.txt ./common/
COPY ./dash/requirements.txt ./
RUN pip install -r ./common/requirements.txt --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

COPY .env .
COPY ./common/ ./common/
COPY ./dash/* ./
COPY ./dash/assets/ ./assets/

RUN ls ./assets

EXPOSE 8000

ENTRYPOINT ["gunicorn", "-w", "1", "-b", ":8000", "app:server"]