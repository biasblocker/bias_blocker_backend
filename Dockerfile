FROM python:3.8-alpine

RUN apk update && apk add bash
RUN apk add --no-cache --update-cache gfortran build-base wget libpng-dev openblas-dev
RUN apk add py3-scipy

WORKDIR /app

COPY app /app/app
COPY prompts /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

EXPOSE 8080

CMD exec uvicorn app.main:app --reload --port 8080 --host 0.0.0.0