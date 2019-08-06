#!/bin/sh

# wait for PSQL server to start
sleep 10

cd project
# prepare init migration
python manage.py makemigrations
# migrate db, so we have the latest db schema
python manage.py migrate
# start gunicorn server
gunicorn --bind :8000 config.wsgi:application

