FROM python:3.13.3-alpine3.21

# Add git
RUN apk update
RUN apk add --no-cache git

COPY . .

RUN pip install -r requirements.txt

RUN crontab crontab

CMD ["cron", "-f"]