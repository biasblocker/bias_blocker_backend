FROM python:3.8-alpine

RUN apk update && apk add bash

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD exec uvicorn app.main:app --reload --port 8080 --host 0.0.0.0