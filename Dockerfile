FROM python:3.12.4-slim

ENV TRACKERID=1

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update

RUN apt-get install -y pkg-config python3-dev default-libmysqlclient-dev build-essential

RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8081

RUN pwd

WORKDIR /app/trackers

RUN python manage.py makemigrations download_tracker

RUN python manage.py migrate


CMD ["python", "manage.py", "runserver", "0.0.0.0:8081"]