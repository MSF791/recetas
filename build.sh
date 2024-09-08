#!/usr/bin/env bash

set -o errexist

pip install -r requirements.txt
python manage.py collectstatic --noinput