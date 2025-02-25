FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN apk add --no-cache bash curl

RUN curl -sS https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /wait-for-it.sh && \
    chmod +x /wait-for-it.sh

CMD /wait-for-it.sh db:5432 -- python manage.py migrate && python manage.py loaddata /app/theatre_dump.json && python manage.py runserver 0.0.0.0:8000
