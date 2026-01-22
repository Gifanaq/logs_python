FROM python:3.12-slim AS build_stage

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENV PATH="$POETRY_HOME/bin:$PATH"
RUN apt-get update && apt-get install -y curl
RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /app
COPY pyproject.toml poetry.lock ./
COPY src /app/src  
COPY scripts /app/scripts

# Установка зависимостей в виртуальное окружение
RUN poetry install --no-root --with main,dev

FROM python:3.12-slim AS app

# Копируем виртуальное окружение из build stage
COPY --from=build_stage /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY src /app/src
COPY scripts /app/scripts

ENTRYPOINT ["python", "-m", "src.main"]

FROM build_stage AS tests
RUN poetry install --no-root --with dev
COPY tests /app/tests
ENTRYPOINT ["poetry", "run", "pytest", "tests"]