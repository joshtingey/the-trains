FROM python:3.8.2-slim-buster

RUN mkdir -p /thetrains_app
WORKDIR /thetrains_app

COPY ./app/common/requirements.txt ./common/
COPY ./app/thetrains_app/requirements.txt ./
RUN pip install -r ./common/requirements.txt --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

COPY .env .
COPY ./app/common/ ./common/
COPY ./app/thetrains_app/* ./thetrains_app/
COPY ./app/thetrains_app/assets/ ./thetrains_app/assets/
COPY ./app/thetrains_app/pages/ ./thetrains_app/pages/

EXPOSE 8000

ENTRYPOINT ["gunicorn", "-w", "4", "-b", ":8000", "thetrains_app.index:server"]