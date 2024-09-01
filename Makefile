build:
	docker build -t agdb-discord-bot:latest .

run-bg:
	docker compose up -d agdb-discord-bot

run:
	docker compose up agdb-discord-bot

stop:
	docker compose down

lint:
	poetry run pre-commit run --all-files

type-check:
	poetry run mypy .

logs:
	docker compose logs -f

shell:
	poetry shell

install:
	POETRY_VIRTUALENVS_IN_PROJECT=1 poetry install --no-root

install-dev:
	POETRY_VIRTUALENVS_IN_PROJECT=1 poetry install --no-root --with dev
	poetry run pre-commit install

uninstall:
	poetry env remove python
