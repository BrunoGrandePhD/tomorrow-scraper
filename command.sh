#!/bin/bash

# Source: https://stackoverflow.com/a/48651061
declare -p | grep -E 'PATH|PG|TOMORROW_API_KEY' > /app/container.env

# Run once on startup to populate the database
(cd /app && python -m tomorrow > /proc/1/fd/1 2>/proc/1/fd/2)

# Run the cron job in the foreground
cron -f
