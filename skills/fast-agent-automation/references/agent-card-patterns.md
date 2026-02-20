# Agent Card-First Patterns

Agent cards are optional in automation.

Use no-card mode (`fast-agent go --message ...`) for simple runs.
Use cards when you need custom instruction and configuration control.

## When to use a card

- Custom system/developer instruction
- MCP server configuration, tool/resource allowlists, and auth setup
- Skill configuration (`skills`, `skills: []`, external skills dirs)
- Child agents / workflow composition
- Pinned defaults (`model`, `request_params`, history files)

## When not to use a card

- Quick smoke tests
- Simple one-off summaries/classification prompts
- Jobs where runtime flags fully describe behavior

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
