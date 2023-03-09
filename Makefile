# Choosing platform-specific shell
ifeq ($(OS), Windows_NT)
SHELL := powershell.exe
.SHELLFLAGS := -NoProfile
PYTHON := python
else
SHELL := bash
PYTHON := python3
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
	$(PYTHON) src/manage.py migrate $(if $m, api $m,) 2>&1

# Creating new migrations
.PHONY: makemigrations
makemigrations:
	$(PYTHON) src/manage.py makemigrations
	sudo chown -R ${USER} src/app/migrations/

# Creating new superuser account
.PHONY: createsuperuser
createsuperuser:
	$(PYTHON) src/manage.py createsuperuser

# Collecting static files into a single location
.PHONY: collectstatic
collectstatic:
	$(PYTHON) src/manage.py collectstatic --no-input

# Starting a development server on port from .env
.PHONY: dev
dev:
	$(PYTHON) src/manage.py runserver 0.0.0.0:${DJANGO_PORT}


# Starting Telegram Bot in polling mode
.PHONY: polling
polling:
	$(PYTHON) src/manage.py polling


# Starting a webhook Telegram Bot
.PHONY: webhook
webhook:
	ngrok config add-authtoken ${NGROK_TOKEN}
	ngrok http ${WEBHOOK_PORT} > /dev/null 2>&1 &
	$(PYTHON) src/manage.py webhook
	kill %1

# Executing manage.py commands in simplified manner 
.PHONY: command
command:
	$(PYTHON) src/manage.py ${c}

# Starting a $(PYTHON) interpreter
.PHONY: shell
shell:
	$(PYTHON) src/manage.py shell

.PHONY: debug
debug:
	$(PYTHON) src/manage.py debug

# Installing dependencies with pipenv 
.PHONY: piplock
piplock:
	pipenv install
	sudo chown -R ${USER} Pipfile.lock

# Flushing DB
.PHONY: flush
flush:
	$(PYTHON) src/manage.py flush --no-input 2>&1

# Running autopep8
.PHONY: autopep8
autopep8:
	autopep8 --in-place --aggressive --aggressive -r src	

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
	$(PYTHON) -m webbrowser -t "http://localhost:${DJANGO_PORT}/admin/" 
	make dev


# Starts DB and Bot Application
.PHONY: docker_run
docker_run: 
	docker-compose up -d

.PHONY: docker_run_build
docker_run_build: 
	docker-compose up -d --build

# Shuts down DB and Bot Application
.PHONY: docker_stop
docker_stop: 
	docker-compose down