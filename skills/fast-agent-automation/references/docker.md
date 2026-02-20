# Docker Reference

## Recommended base strategy

Prefer pinned Python 3.13 patch version plus Astral `uv` binary.

Reason: fast-agent currently requires Python `>=3.13.5,<3.14`.

Current recommendation status:

- ✅ Use `python:3.13.x-slim-bookworm` as base (pin patch for repeatability)
- ✅ Copy `uv`/`uvx` from `ghcr.io/astral-sh/uv:latest`
- ⚠️ Do not assume `hf jobs uv` default image fits this requirement in every case
  (HF docs currently show a Python 3.12 uv default image for UV jobs)

## Minimal Dockerfile

```dockerfile
FROM python:3.13.7-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN uv pip install --system --no-cache fast-agent-mcp

COPY . /app

# Optional for MCP server mode
EXPOSE 7860

CMD ["fast-agent", "go", "--message", "health check", "--results", "/tmp/health.json"]
```

## Serve mode container

```dockerfile
CMD [
  "fast-agent", "serve",
  "--card", "agent.md",
  "--transport", "http",
  "--host", "0.0.0.0",
  "--port", "7860"
]
```

## Build/run quickstart

```bash
docker build -t fast-agent-auto .
docker run --rm \
  -e OPENAI_API_KEY \
  -e ANTHROPIC_API_KEY \
  fast-agent-auto
```
