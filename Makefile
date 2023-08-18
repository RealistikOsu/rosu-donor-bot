#!/usr/bin/make

build: # build all containers
	if [ -d "pgdata" ]; then sudo chmod -R 755 pgdata; fi
	docker build -t rosu-donor-bot:latest -t rosu-donor-bot:latest .

run-bg: # run all containers in the background
	docker-compose up -d rosu-donor-bot

run: # run all containers in the foreground
	docker-compose up rosu-donor-bot

stop: # stop all containers
	docker-compose down

lint: # run pre-commit hooks
	pre-commit run -a

logs: # attach to the containers live to view their logs
	docker-compose logs -f

shell:
	docker-compose exec -it rosu-donor-bot bash

test: # run the tests
	docker-compose exec rosu-donor-bot /scripts/run-tests.sh

test-dbg: # run the tests in debug mode
	docker-compose exec rosu-donor-bot /scripts/run-tests.sh --dbg

view-cov: # open the coverage report in the browser
	if grep -q WSL2 /proc/sys/kernel/osrelease; then \
		wslview tests/htmlcov/index.html; \
	else \
		xdg-open tests/htmlcov/index.html; \
	fi

up-migrations: # apply up migrations from current state
	docker-compose exec rosu-donor-bot /scripts/migrate-db.sh up

down-migrations: # apply down migrations from current state
	docker-compose exec rosu-donor-bot /scripts/migrate-db.sh down

up-seeds: # apply up seeds from current state
	docker-compose exec rosu-donor-bot /scripts/seed-db.sh up

down-seeds: # apply down seeds from current state
	docker-compose exec rosu-donor-bot /scripts/seed-db.sh down
