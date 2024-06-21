FROM python:3.10-alpine3.20
LABEL authors="p4niQ"

ENV PYTHONUNBUFFERED 1

WORKDIR /theatre_app

ENV PYTHONPATH=${PYTHONPATH}:/theatre_app/management/commands

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .
