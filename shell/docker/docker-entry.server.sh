#!/bin/sh

# Making migrations
echo -e "\e[1;34mApplying migrations...\e[0m"
python src/manage.py migrate --no-input

# Collecting static files
echo -e "\e[1;34mCollecting static files...\e[0m"
python src/manage.py collectstatic --no-input

# Creating test admin user
echo -e "\e[1;34mCreating Django superuser...\e[0m"
python src/manage.py createsuperuser --no-input

# Starting Gunicorn 
echo -e "\e[1;34mStarting Gunicorn Application server...\e[0m"
gunicorn --bind 0.0.0.0:$DJANGO_PORT --workers=4 --chdir src config.wsgi:application &


# Starting bot in polling mode 
echo -e "\e[1;34mStarting Telegram Bot in polling mode\e[0m"
python src/manage.py polling