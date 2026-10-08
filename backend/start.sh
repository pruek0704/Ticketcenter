#!/bin/sh
set -eu
if [ -z "${DATABASE_URL:-}" ]; then
  DATABASE_URL="$(python -c 'import os, urllib.parse; print("postgresql+psycopg://%s:%s@%s:5432/%s" % (os.environ["DB_USER"], urllib.parse.quote(os.environ["DB_PASSWORD"], safe=""), os.environ["DB_HOST"], os.environ["DB_NAME"]))')"
  export DATABASE_URL
fi
alembic upgrade head
python -m app.seed
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
