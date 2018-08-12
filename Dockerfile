FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
  mongo-tools

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD python app.py
