#!/usr/bin/env bash

echo "Running Python tests..."
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"settings.test"}
python manage.py test $1