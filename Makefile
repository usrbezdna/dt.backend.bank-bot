# Choosing platform-specific shell
ifeq ($(OS), Windows_NT)
SHELL := powershell.exe
.SHELLFLAGS := -NoProfile
else
SHELL := bash
endif

# Exporting environmental variables from .env file
# We'll then use ${PORT} in our make targets
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Applying migrations to database
.PHONY: migrate
migrate:
	python src/manage.py migrate $(if $m, api $m,)

# Creating new migrations
.PHONY: makemigrations
makemigrations:
	python src/manage.py makemigrations
	sudo chown -R ${USER} src/app/migrations/

# Creating new superuser account
.PHONY: createsuperuser
createsuperuser:
	python src/manage.py createsuperuser

# Collecting static files into a single location
.PHONY: collectstatic
collectstatic:
	python src/manage.py collectstatic --no-input

# Starting a development server on port from .env
.PHONY: dev
dev:
	python src/manage.py runserver localhost:${PORT}

# Starting a webhook Telegram Bot
.PHONY: webhook
webhook:
	python src/manage.py webhook

# Executing manage.py commands in simplified manner 
.PHONY: command
command:
	python src/manage.py ${c}

# Starting a python interpreter
.PHONY: shell
shell:
	python src/manage.py shell

.PHONY: debug
debug:
	python src/manage.py debug

# Installing dependencies with pipenv 
.PHONY: piplock
piplock:
	pipenv install
	sudo chown -R ${USER} Pipfile.lock

# Running code linters
.PHONY: lint
lint:
	isort .
	flake8 --config setup.cfg
	black --config pyproject.toml .

# Lint checking 
.PHONY: check_lint
check_lint:
	isort --check --diff .
	flake8 --config setup.cfg
	black --check --config pyproject.toml .

# Starts dev server and opens admin panel in browser
.PHONY: admin
admin: 
	python -m webbrowser -t "http://localhost:${PORT}/admin/" 
	make dev