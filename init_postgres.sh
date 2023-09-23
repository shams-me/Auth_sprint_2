#!/bin/bash

#!/bin/bash

echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DB: $POSTGRES_DB"
echo "Current pg_hba.conf:"
cat /etc/postgresql/pg_hba.conf

wait_for_service() {
  host="$1"
  port="$2"

  echo "Waiting for $host:$port..."

  while ! nc -z "$host" "$port"; do
    sleep 1
  done

  echo "$host:$port is available."
}

wait_for_service postgres 5432

echo "host $POSTGRES_DB $POSTGRES_USER all md5" >> /etc/postgresql/pg_hba.conf

# Start PostgreSQL
exec docker-entrypoint.sh postgres
