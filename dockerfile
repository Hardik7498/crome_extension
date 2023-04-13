FROM python:3.8

WORKDIR /newapp

COPY requirements.txt requirements.txt
COPY dev-requirements.txt dev-requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=src.app:create_app
