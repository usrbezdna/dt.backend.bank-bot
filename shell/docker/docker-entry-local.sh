#!/bin/sh

# Making migrations
echo -e "\e[1;34mApplying migrations...\e[0m"
python src/manage.py migrate --no-input

# Creating test admin user
echo -e "\e[1;34mCreating Django superuser...\e[0m"
python src/manage.py createsuperuser --no-input

# Starting frontend 
echo -e "\e[1;34mStarting Django HTTP server...\e[0m"
python src/manage.py runserver 0.0.0.0:$DJANGO_PORT &

# Starting bot in polling mode 
echo -e "\e[1;34mStarting Telegram Bot in polling mode\e[0m"
python src/manage.py polling