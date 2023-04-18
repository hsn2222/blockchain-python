FROM python:3.7-slim

WORKDIR /app
ENV FLASK_APP=app

COPY /app/requirements.txt ./

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt