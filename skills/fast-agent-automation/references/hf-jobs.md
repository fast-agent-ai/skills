# Hugging Face Jobs Reference

Use Hugging Face Jobs for one-off or scheduled fast-agent automation.

## `fast-agent` invocation style in Jobs

When using `hf jobs uv run`, run commands as `fast-agent <subcommand>` after `--`.

## Prereqs

- Install CLI with jobs support (`hf`)
- Authenticate: `hf auth login`
- Ensure account plan includes Jobs access

## Execution modes for Jobs

- No-card mode: use runtime flags only (`--model`, `--message`, `--prompt-file`, `--results`)
- Card mode: add `--card` and optional `--agent` when custom instruction/config is needed

## One-off CPU job (card mode)

```bash
hf jobs uv run \
  --python 3.13 \
  --with fast-agent-mcp \
  --flavor cpu-basic \
  --timeout 2h \
  --secrets HF_TOKEN \
  --secrets OPENAI_API_KEY \
  -- fast-agent go \
     --card cards \
     --agent automation \
     --model sonnet \
     --message "Run cloud summary" \
     --results result.json
```

## Kimi smoke test (one-off, no-card)

Minimal end-to-end check for model routing + artifact output:

```bash
hf jobs uv run \
  --python 3.13 \
  --with fast-agent-mcp \
  --flavor cpu-basic \
  --timeout 20m \
  --secrets HF_TOKEN \
  --secrets OPENROUTER_API_KEY \
  --secrets MOONSHOT_API_KEY \
  -- fast-agent go \
     --model kimi \
     --message "HF Job smoke test: reply with exactly OK" \
     --results result.json
```

Expected signal:

- Job status reaches `COMPLETED`
- Output contains `OK`
- `result.json` is produced with assistant message history

## Scheduled job

```bash
hf jobs scheduled uv run @hourly \
  --python 3.13 \
  --with fast-agent-mcp \
  --flavor cpu-basic \
  --secrets HF_TOKEN \
  --secrets OPENAI_API_KEY \
  -- fast-agent go \
     --card cards \
     --agent automation \
     --message "Hourly status" \
     --results result.json
```

## Secret safety policy

Before submitting Jobs, enumerate candidate env vars and ask user confirmation.
Never silently forward local secrets.

Suggested candidate list:

- `HF_TOKEN`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- provider-specific model keys requested by the user

## MCP alternative

Hugging Face MCP server includes job-management tools. Prefer CLI examples first for reproducibility unless user specifically requests MCP-invoked job control.
