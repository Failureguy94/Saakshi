FROM python:3.12-slim

# Install system dependencies (build-essential, curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official binary
COPY --from=ghcr.io/astral-sh/uv:0.4.17 /uv /bin/uv

WORKDIR /app

# Copy dependency definition
COPY pyproject.toml ./

# Install dependencies into virtual environment
RUN uv venv /opt/venv && uv pip install --no-cache -e ".[dev]"

ENV PATH="/opt/venv/bin:$PATH"

# Copy application source code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
