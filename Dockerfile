# Build stage
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    shared-mime-info \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv
WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

ENV UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY src/ ./src/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Runtime stage
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libcairo2 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/uv.lock /app/README.md ./

RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app

USER botuser

CMD ["uv", "run", "--module", "apisbot"]
