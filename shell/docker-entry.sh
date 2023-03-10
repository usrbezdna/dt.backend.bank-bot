#!/bin/sh

# Making migrations
python src/manage.py migrate

# Creating test admin user
python src/manage.py createsuperuser --no-input

# Starting frontend 
python src/manage.py runserver 0.0.0.0:$DJANGO_PORT &

# Starting bot in polling mode 
python src/manage.py polling