# Set default environment to 'local' if none is provided
ENV ?= local

# Default target: show available commands when no target is specified
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make up ENV=local|prod                            - Bring up the services with Docker Compose (--build)"
	@echo "  make down ENV=local|prod                          - Bring down the services"
	@echo "  make createsuperuser ENV=local|prod               - Create a Django superuser"
	@echo "  make makemigrations ENV=local|prod                - Make Django migrations"
	@echo "  make migrate ENV=local|prod                       - Apply Django migrations"
	@echo "  make shell ENV=local|prod                         - Start Django shell"
	@echo "  make pytest                                       - Run pytest for unit testing (local)"
	@echo "  make coverage                                     - Run tests with coverage collection (local)"
	@echo "  make coverage-report                              - Generate and display coverage report (local)"


# Command to bring up the services with --build option based on the environment
up:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml up --build -d
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml up --build -d
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to bring down the services based on the environment
down:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml down
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml down
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to run createsuperuser with the appropriate docker-compose file
createsuperuser:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py createsuperuser
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml run --rm django python manage.py createsuperuser
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

makemigrations:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py makemigrations
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml run --rm django python manage.py makemigrations
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to run migrate with the appropriate docker-compose file
migrate:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml run --rm django python manage.py migrate
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml run --rm django python manage.py migrate
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to run Django shell with the appropriate docker-compose file
shell:
ifeq ($(ENV),local)
	@docker compose -f docker-compose.local.yaml run --rm django bash
else ifeq ($(ENV),prod)
	@docker compose -f docker-compose.production.yaml run --rm django bash
else
	@echo "Invalid ENV value! Please specify ENV=local or ENV=prod."
	exit 1
endif

# Command to run pytest for unit testing
test:
	@docker compose -f docker-compose.local.yaml run --rm django pytest

testk:
	@docker compose -f docker-compose.local.yaml run --rm django pytest -k $(k)

# Command to run pytest with coverage for test coverage analysis
coverage:
	@docker compose -f docker-compose.local.yaml run --rm django coverage run -m pytest

# Command to generate and display a test coverage report
coverage-report:
	@docker compose -f docker-compose.local.yaml run --rm django coverage report

# Command to generate a test coverage report in HTML format
coverage-html:
	@docker compose -f docker-compose.local.yaml run --rm django coverage html
