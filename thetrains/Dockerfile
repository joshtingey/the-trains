FROM python:3.8.2-slim-buster

RUN mkdir -p /thetrains
WORKDIR /thetrains

COPY ./common/requirements.txt ./common/
COPY ./thetrains/requirements.txt ./
RUN pip install -r ./common/requirements.txt --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

COPY .env .
COPY ./common/ ./common/
COPY ./thetrains/* ./thetrains/
COPY ./thetrains/assets/ ./thetrains/assets/
COPY ./thetrains/pages/ ./thetrains/pages/

EXPOSE 8000

ENTRYPOINT ["gunicorn", "-w", "4", "-b", ":8000", "thetrains.index:server"]