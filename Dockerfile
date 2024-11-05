FROM python:3.12.4-slim



ENV TRACKERID=1123
ENV ISLOGINREQUIRED=1
ENV DB_NAME=test_torrent
ENV DB_USER=root
ENV DB_PASSWORD=admin
ENV DB_HOST=host.docker.internal
ENV DB_PORT=3306
ENV SERVER_PORT=8081

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update

RUN apt-get install -y pkg-config python3-dev default-libmysqlclient-dev build-essential

RUN pip install -r requirements.txt

COPY . /app/

EXPOSE ${SERVER_PORT}

RUN pwd

WORKDIR /app/trackers

RUN python manage.py makemigrations download_tracker

RUN python manage.py migrate

# NHO SỬA CÁI PORT CHỖ NÀY
CMD ["python", "manage.py", "runserver", "0.0.0.0:8081"]