FROM python:3.8.2-slim-buster

RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt /app

RUN pip install -r requirements.txt --no-cache-dir

EXPOSE 8000

COPY . /app

ENTRYPOINT ["gunicorn", "-w", "1", "-b", ":8000", "app:server"]