include .env
ALEMBIC = docker compose exec fastapi /app/.venv/bin/alembic -c /app/backend/alembic.ini
DATABASE_PORT ?= 5432

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: up
up:
	docker compose up --build

.PHONY: revision
revision:
	$(ALEMBIC) revision --autogenerate -m "$(message)"

.PHONY: upgrade
upgrade:
	$(ALEMBIC) upgrade head

.PHONY: downgrade
downgrade:
	$(ALEMBIC) downgrade -1

.PHONY: downgrade-base
downgrade-base:
	$(ALEMBIC) downgrade base

.PHONY: superuser
superuser:
	docker compose exec fastapi /app/.venv/bin/python /app/backend/src/users/presentation/create_superuser.py --username "$(username)" --email "$(email)" --password "$(password)"

.PHONY: test
test:
	docker compose exec fastapi /app/.venv/bin/pytest -v -rs --capture=no --disable-warnings

load-test:
	docker compose exec fastapi /app/.venv/bin/locust -f /app/backend/test/tests/locustfile.py

.PHONY: db-connect
db-connect:
	docker compose exec postgres psql -h localhost -p "$(DATABASE_PORT)" -U "$(DATABASE_USERNAME)" -d "$(DATABASE_NAME)" --pset pager=off
