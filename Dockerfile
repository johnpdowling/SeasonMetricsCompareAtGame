FROM python:3.13.3-alpine3.21

# Add git & cronie
RUN apk update
RUN apk add --no-cache git cronie

COPY . .

# Create pybaseball's cache directory
ENV PYBASEBALL_CACHE=/cache
RUN mkdir -p /cache

# Create config directory
ENV CONFIG_FILE_PATH=/config/config.yaml
ENV SECRETS_FILE_PATH=/config/secrets.yaml
RUN mkdir -p /config

# Create volumes
VOLUME [ "/cache" ]
VOLUME [ "/config" ]

RUN pip install --no-cache-dir -r requirements.txt

RUN crontab crontab

# Get the entrypoint script ready to go
RUN chmod +x /entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
CMD ["crond", "-f"]