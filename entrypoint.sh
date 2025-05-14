#!/bin/sh

# Check whether the config file exists, creating it with default values if it doesn't
CONFIG_FILE_PATH=${CONFIG_FILE_PATH:-/config/config.yaml}
if [ ! -f "$CONFIG_FILE_PATH" ]; then
    echo "Creating default config file at $CONFIG_FILE_PATH"
    cat <<EOL > "$CONFIG_FILE_PATH"
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

# Check whether the secrets file exists, creating it with default values if it doesn't
SECRETS_FILE_PATH=${SECRETS_FILE_PATH:-/config/secrets.yaml}
if [ ! -f "$SECRETS_FILE_PATH" ]; then
    echo "Creating default secrets file at $SECRETS_FILE_PATH"
    cat <<EOL > "$SECRETS_FILE_PATH"
bluesky:
  username: "USERNAME.bsky.social"
  password: "PASSWORD"
EOL
fi
# Execute the passed command
exec "$@"