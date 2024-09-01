FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /srv/root

COPY pyproject.toml poetry.lock ./
RUN pip install -U pip poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

COPY scripts /scripts
RUN chmod u+x /scripts/*

COPY . .

ENTRYPOINT ["/scripts/run-bot.sh"]
