#!/bin/bash

# May be useful in future scripts

for dir in ./src/app/internal/api_v1/*; do
    if [ -d "$dir" ]; then
        mkdir "$dir"/db "$dir"/domain "$dir"/presentation

        touch "$dir"/db/models.py "$dir"/db/repositories.py 
        touch "$dir"/domain/entities.py "$dir"/domain/services.py

        touch "$dir"/presentation/admin.py "$dir"/presentation/handlers.py "$dir"/presentation/routers.py
        touch "$dir"/api.py
    fi
done