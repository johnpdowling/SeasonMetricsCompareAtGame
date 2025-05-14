#!/bin/sh

# Enforce the environment variable so it's always routed to the VOLUME mount point
export PYBASEBALL_CACHE=/cache

# Check whether the config file exists, creating it with default values if it doesn't
if [ ! -f /config/config.yaml ]; then
    echo "Creating default config file at /config/config.yaml"
    cat <<EOL > /config/config.yaml
diffs:
- team: CHA
  year: 2025
  games_played: 0
pairs:
- teamA: CHA
  yearA: 2024
  colorA: red
  teamB: CHA
  yearB: 2025
  colorB: black
  games_played: 0
EOL
fi
export CONFIG_FILE_PATH=/config/config.yaml

# Check whether the secrets file exists, creating it with default values if it doesn't
if [ ! -f /config/secrets.yaml ]; then
    echo "Creating default secrets file at /config/secrets.yaml"
    cat <<EOL > /config/secrets.yaml
bluesky:
  username: "USERNAME.bsky.social"
  password: "PASSWORD"
EOL
fi
export SECRETS_FILE_PATH=/config/secrets.yaml
# Execute the passed command
exec "$@"