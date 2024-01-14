#!/bin/bash -eux

# FIXME: ugly wait until DB is ready and created
sleep 5

python3 manage.py collectstatic --noinput --clear
python3 manage.py compilemessages
python3 manage.py makemigrations
python3 manage.py migrate

exec "$@"
