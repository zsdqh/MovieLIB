ALEMBIC = docker compose exec fastapi /app/.venv/bin/alembic -c /app/backend/alembic.ini

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

.PHONY: superuser
superuser:
	docker compose exec fastapi /app/.venv/bin/python /app/backend/src/auth/users/presentation/create_superuser.py --username "$(username)" --email "$(email)" --password "$(password)"

.PHONY: test
test:
	docker compose exec fastapi /app/.venv/bin/pytest -v -rs --capture=no --disable-warnings
