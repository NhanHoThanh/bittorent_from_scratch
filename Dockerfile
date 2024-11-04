FROM python:3.12.4-slim

ENV TRACKERID=1

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8081

RUN python manage.py makemigrations trackers

RUN python manage.py migrate


CMD ["python", "manage.py", "runserver", "0.0.0.0:8081"]