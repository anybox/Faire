.PHONY: init watch help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

init: ## install project in the current python environnement in develop mode
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

setup-dev: ## setup test database in order to be ready to launch
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	$(call wait_db)
	docker-compose \
		-f docker-compose.yml -f docker-compose.dev.yml run clocky bash -c \
			"cd install_update && \
			psql postgresql://clocky:clocky_password@db:5432/clocky -a -f prod_install.sql && \
			psql postgresql://clocky:clocky_password@db:5432/clocky -a -f develop_install.sql"

run: ## Locally run the application
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

test-unit-backend: ## Launch backend unit tests only
	docker-compose \
		-f docker-compose.yml -f docker-compose.dev.yml run clocky bash -c \
			"rm cra/*; \
			nosetests --tests clocky/tests -s -v --with-coverage --cover-erase --cover-html --cover-package clocky"

test-unit-frontend:  ## Launch frontend unit tests only
	docker-compose \
		-f docker-compose.yml -f docker-compose.dev.yml run frontend npm run test

clean: ## Clean cache files, docker containers and docker volumes
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v --remove-orphans || /bin/true

psql: ## Get a psql shell
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec db psql -U clocky clocky

define wait_db
	docker run --rm \
		-v ${PWD}/wait-for-it.sh:/tmp/wait-for-it.sh \
		--network clocky_internal \
		python:3 \
		/tmp/wait-for-it.sh db:5432 -s -t 30 -- echo Postgresql is ready \
	|| (docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs --tail 100 db ; echo "Postresql wasn't ready in the given time"; exit 1)
endef
