#!/usr/bin/env bash
set -e

command="$*"
if [[ "$command" == *"gunicorn"* ]] || [[ "$command" == *"manage.py runserver"* ]]; then
  uv run python manage.py migrate --noinput
fi

exec "$@"
