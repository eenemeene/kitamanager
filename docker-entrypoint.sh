#!/bin/bash -eux

python3 manage.py collectstatic --noinput --clear
python3 manage.py makemigrations
python3 manage.py migrate

exec "$@"
