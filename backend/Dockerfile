FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.9.22 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN addgroup --system vigi \
    && adduser --system --ingroup vigi --home /app vigi \
    && mkdir -p /app/data \
    && chown -R vigi:vigi /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=vigi:vigi . .

ENV PATH="/app/.venv/bin:$PATH"

USER vigi

EXPOSE 8000

CMD ["sh", "-c", "uv run --frozen --no-dev alembic upgrade head && exec uv run --frozen --no-dev uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
