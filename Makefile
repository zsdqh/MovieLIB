ALEMBIC = docker compose exec fastapi-auth /app/.venv/bin/alembic -c /app/backend/alembic.ini

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
