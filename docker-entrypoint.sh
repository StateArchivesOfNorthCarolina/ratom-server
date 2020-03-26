#!/bin/sh
set -e

if [ -n "${DATABASE_URL+set}" ]; then
until psql $DATABASE_URL -c '\l'; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done
fi

>&2 echo "Postgres is up - continuing"

exec "$@"
