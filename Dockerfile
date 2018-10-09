FROM python:3.6
ENV PYTHONUNBUFFERED 1

ADD . /dungeon_brawl
WORKDIR /dungeon_brawl

RUN pip install -r requirements.txt
