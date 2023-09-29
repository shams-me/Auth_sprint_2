#!/bin/bash

set -e

chown www-data:www-data /var/log

wait_for_service() {
  host="$1"
  port="$2"

  echo "Waiting for $host:$port..."

  while ! nc -z "$host" "$port"; do
    sleep 1
  done

  echo "$host:$port is available."
}

wait_for_service "$POSTGRES_HOST" "$POSTGRES_PORT"

python3 manage.py migrate --no-input

uwsgi --strict --ini /opt/app/uwsgi.ini
