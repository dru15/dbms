.PHONY: up down reset seed-bulk test psql ui query run-q

DB_SERVICE := db
DB_USER := postgres
DB_NAME := disaster_relief

up:
	docker compose up -d
	@echo "Waiting for PostgreSQL to be ready..."
	@until docker compose exec -T $(DB_SERVICE) pg_isready -U $(DB_USER) -d $(DB_NAME) > /dev/null 2>&1; do \
		sleep 1; \
	done
	@echo "PostgreSQL is ready."

down:
	docker compose down

reset: up
	@echo "Resetting database schema and seed..."
	@docker compose exec -T $(DB_SERVICE) psql -U $(DB_USER) -d $(DB_NAME) -f /db/00_roles.sql
	@docker compose exec -T $(DB_SERVICE) psql -U $(DB_USER) -d $(DB_NAME) -f /db/01_schema.sql
	@if [ -f db/02_seed.sql ]; then \
		echo "Applying seed data..."; \
		docker compose exec -T $(DB_SERVICE) psql -U $(DB_USER) -d $(DB_NAME) -f /db/02_seed.sql; \
	fi
	@echo "Database reset complete."

seed-bulk: up
	@if [ -f db/03_seed_bulk.sql ]; then \
		echo "Applying bulk seed data..."; \
		docker compose exec -T $(DB_SERVICE) psql -U $(DB_USER) -d $(DB_NAME) -f /db/03_seed_bulk.sql; \
		echo "Bulk seed complete."; \
	else \
		echo "Error: db/03_seed_bulk.sql not found."; \
		exit 1; \
	fi

test:
	@python3 tests/runner.py

psql:
	docker compose exec $(DB_SERVICE) psql -U $(DB_USER) -d $(DB_NAME)

query:
	@docker compose exec -T $(DB_SERVICE) psql -U $(DB_USER) -d $(DB_NAME) -c "$(SQL)"

run-q:
	@file=$$(echo "$(Q)" | sed 's/^Q//'); \
	docker compose exec -T $(DB_SERVICE) psql -U $(DB_USER) -d $(DB_NAME) -f "/db/queries/Q$$file.sql"

ui: up
	@echo "Starting SQL Lab Web UI on http://localhost:3001 ..."
	@export NVM_DIR="$$HOME/.nvm" && [ -s "$$NVM_DIR/nvm.sh" ] && . "$$NVM_DIR/nvm.sh" && nvm use 20 && cd ui/server && npm start

