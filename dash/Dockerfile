FROM python:3.6.7

RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

COPY . /app

ENTRYPOINT ["gunicorn", "-w", "1", "-b", ":8000", "app:server"]