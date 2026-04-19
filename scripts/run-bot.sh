#!/usr/bin/env bash
set -eo pipefail

if [ -n "$KUBERNETES" ]; then
    source /vault/secrets/secrets.txt
fi

if [ -z "$APP_ENV" ]; then
  echo "Please set APP_ENV"
  exit 1
fi


if [ -z "$APP_COMPONENT" ]; then
  echo "Please set APP_COMPONENT"
  exit 1
fi

cd /srv/root

# ensure database exists
# /scripts/init-db.sh

# run sql database migrations & seeds
# /scripts/migrate-db.sh up
# /scripts/seed-db.sh up

exec app/main.py
