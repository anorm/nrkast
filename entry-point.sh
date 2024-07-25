#!/bin/sh

set -e

export YOYO_DATABASE=$(echo $DB_CONNECTION | sed -e "s/postgresql:/postgresql+psycopg:/g")
echo $YOYO_DATABASE
yoyo apply
uvicorn --host 0.0.0.0 --port $PORT nrkast.server:app
