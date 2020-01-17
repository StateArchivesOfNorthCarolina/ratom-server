#!/bin/bash
set -ex
# Check migrations
python manage.py makemigrations --dry-run | grep 'No changes detected' || (echo 'There are changes which require migrations.' && exit 1)

python manage.py test -v2
