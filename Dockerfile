FROM python:3.6
ENV PYTHONUNBUFFERED 1

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD python populate.py && python app.py
