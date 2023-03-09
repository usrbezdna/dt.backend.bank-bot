#!/bin/sh

# Making migrations
make migrate

# Starting frontend 
make dev &

# Starting bot in polling mode 
make polling