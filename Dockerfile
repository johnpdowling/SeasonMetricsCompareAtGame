FROM python:3.13.3-alpine3.21

COPY . .

RUN pip install -r requirements.txt

RUN crontab crontab

CMD ["cron", "-f"]