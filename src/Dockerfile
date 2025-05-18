FROM python:3.13-slim-bookworm AS base


FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.7.2 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app
COPY uv.lock pyproject.toml /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev

COPY src/ /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev


FROM base
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
