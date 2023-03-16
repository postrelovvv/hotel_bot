FROM python:3.9-bullseye as pybase

WORKDIR /app

ARG LANDSCAPE \
    UID=1000 \
    GID=1000

RUN groupadd -g "${GID}" -r web \
  && useradd -d '/app' -g web -l -r -u "${UID}" web \
  && chown web:web -R '/app'


RUN pip install poetry

COPY ../poetry.lock ../pyproject.toml ./

RUN poetry config virtualenvs.create false \
  && poetry install $(test "$LANDSCAPE" == production && echo "--no-dev") --no-interaction --no-ansi

COPY --chown=web:web ./docker/entrypoint.sh .
COPY --chown=web:web ./src ./src
RUN chmod +x './entrypoint.sh'

USER web

ENTRYPOINT ./entrypoint.sh

