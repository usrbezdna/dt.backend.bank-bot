#!/bin/sh

# Making migrations
make migrate

# Creating test admin user
export DJANGO_SUPERUSER_USERNAME=testadmin
export DJANGO_SUPERUSER_PASSWORD=testpass
export DJANGO_SUPERUSER_EMAIL=test@mail.com
make superuser

# Starting frontend 
make dev &

# Starting bot in polling mode 
make polling 