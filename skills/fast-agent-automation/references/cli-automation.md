# CLI Automation Reference

## Runtime requirements

- Package: `fast-agent-mcp`
- Python: `>=3.13.5,<3.14`

## Primary command

Use `fast-agent go` for automation.

## Execution modes

### 1) Default agent/instruction (no card)

Use when you want simple execution and runtime-driven prompts/models.

```bash
fast-agent go --model sonnet --message "Quick summary" --results out.json
```

### 2) Card-based agent (`--card`, optional `--agent`)

Use when you need custom instruction, MCP servers/tools, skill controls, or agent workflows.

```bash
fast-agent go --card ./cards --agent automation --model sonnet --message "Nightly run" --results out.json
```

Core options:

- `--message`, `-m`: send text and exit interactive mode
- `--prompt-file`, `-p`: load prompt from text/JSON file
- `--results`: export resulting history to file
- `--model`, `--models`: single model or comma-separated list for fan-out
- `--agent`: target a specific agent by name
- `--agent-cards`, `--card`: load one or more agent card paths/URLs
- `--servers`: enable configured server names
- `--url` + `--auth`: connect to HTTP/SSE MCP servers
- `--npx` / `--uvx` / `--stdio`: attach ad-hoc stdio MCP servers
- `--skills-dir` / `--skills`: override default skills directory resolution
- `--resume`: resume last/specified session
- `--noenv`: disable implicit environment side effects

## Output contract (important)

### Terminal output

- Human-facing output for current execution.
- In simple `--message` flow, prints returned assistant text.
- In parallel model flow without a specific target agent, prints formatted parallel display.

### `--results`

- Persists selected agent histories.
- If file extension is `.json`, writes enhanced structured message JSON.
- Non-JSON path writes delimited text format.
- In multi-model fan-out without `--agent`, writes per-model suffixed files.

## Recommended CI recipe

No-card mode:

```bash
set -euo pipefail

mkdir -p artifacts

fast-agent go \
  --model sonnet \
  --message "Run the nightly summary" \
  --results artifacts/nightly.json

test -s artifacts/nightly.json
```

Card mode:

```bash
set -euo pipefail

mkdir -p artifacts

fast-agent go \
  --card ./cards \
  --agent automation \
  --model sonnet \
  --message "Run the nightly summary" \
  --results artifacts/nightly.json

test -s artifacts/nightly.json
```

## Model fan-out behavior

Use comma-separated models:

```bash
fast-agent go --model "haiku,sonnet,gpt-4" ... --results out.json
```

Expect per-model files:

- `out-haiku.json`
- `out-sonnet.json`
- `out-gpt-4.json`

If names sanitize to collisions, numeric suffixes are appended.

## Model precedence and best practice

Model resolution precedence includes explicit agent model values from cards/decorators above CLI
`--model`.

Practical implications:

- No-card mode: CLI `--model` is the active model selector.
- If your selected agent card defines `model: sonnet`, passing `--model haiku` will not override
  that explicit card model for that agent.
- For minimal automation that needs runtime model selection, keep card agents model-agnostic
  (omit `model`) and pass `--model` at invocation.
- Use card-pinned models only when you intentionally want fixed behavior.
