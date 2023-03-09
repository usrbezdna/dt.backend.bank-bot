#!/bin/sh

# Making migrations
python src/manage.py migrate

# Creating test admin user
export DJANGO_SUPERUSER_USERNAME=testadmin
export DJANGO_SUPERUSER_PASSWORD=testpass
export DJANGO_SUPERUSER_EMAIL=test@mail.com
python src/manage.py createsuperuser --no-input

# Starting frontend 
python src/manage.py runserver 0.0.0.0:8080 &

# Starting bot in polling mode 
python src/manage.py polling