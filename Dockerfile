FROM python:3.10.17-alpine3.22

COPY . .

RUN pip install -r requirements.txt

RUN crontab crontab

CMD ["cron", "-f"]