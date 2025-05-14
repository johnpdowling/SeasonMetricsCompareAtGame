FROM python:3.13.3-alpine3.21

# Add git & cronie
RUN apk update
RUN apk add --no-cache git cronie

COPY . .

# Create pybaseball's cache directory
RUN mkdir -p /cache

# Create config directory
RUN mkdir -p /config

# Create volumes
VOLUME [ "/cache" ]
VOLUME [ "/config" ]

RUN pip install --no-cache-dir -r requirements.txt

# Create log directory
RUN mkdir -p /var/log

RUN crontab crontab

# Get our python script ready to go
RUN chmod +x /SeasonMetricsCompareAtGame.py
# Get the entrypoint script ready to go
RUN chmod +x /entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
CMD ["crond", "-f"]