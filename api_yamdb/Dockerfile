FROM python:3.7-slim

ENV APP=/home/app

WORKDIR $APP

RUN pip3 install --upgrade pip

COPY ./. .

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]
