FROM python:3.6.7

RUN mkdir -p /collector
WORKDIR /collector
COPY requirements.txt /collector
RUN pip install --no-cache-dir -r requirements.txt

COPY . /collector

ENTRYPOINT ["python", "-u", "collector.py"]