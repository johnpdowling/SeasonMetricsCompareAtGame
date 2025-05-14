FROM python:3.13.3-alpine3.21

# Add git
RUN apk update
RUN apk add --no-cache git

COPY . .

# Create pybaseball's cache directory
RUN mkdir -p /cache

# Create config directory
RUN mkdir -p /config

# Create volumes
VOLUME [ "/cache" ]
VOLUME [ "/config" ]

RUN pip install -r requirements.txt

RUN crontab crontab

# Get the entrypoint script ready to go
RUN chmod +x /entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
CMD ["cron", "-f"]