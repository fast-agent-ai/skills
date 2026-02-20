# Agent Card-First Patterns

Prefer an agent card as the control plane for automation.

## Minimal automation card

```yaml
---
type: agent
name: automation_orchestrator
default: true
mcp_connect:
  - target: "https://hf.co/mcp"
    name: "hf_hub"
servers:
  - filesystem
---

Run deterministic automation tasks.
Always write machine-readable artifacts with --results.
Always confirm before exporting local env vars as job secrets.
```

## Why this pattern

- centralizes model + instruction + server connections
- reduces duplicated CLI flags
- makes local, Docker, and cloud execution consistent

## Model pinning guidance

- Omit `model` in this card when you want runtime `--model` control in automation.
- Add `model` only when you need a pinned default and are okay with card-level lock-in.

## Tool-card pattern

Keep reusable external integrations in tool-only cards, then attach with `--card-tool`.
This keeps orchestration instruction cleaner and easier to version.
