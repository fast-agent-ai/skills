---
name: fast-agent-automation
description: Automate fast-agent runs from CLI, Docker, and Hugging Face Jobs. Use when users need repeatable non-interactive execution (`fast-agent go --message` / `--prompt-file`), deterministic artifact handling (`--results`), multi-model fan-out, containerization with uv, or scheduled/cloud execution with hf jobs and secrets management.
---

# Fast-Agent Automation

Build repeatable automation around `fast-agent` CLI, container, and cloud job execution.

## Use this workflow

1. Collect execution target:
   - local CLI
   - Docker container
   - Hugging Face Job (one-off or scheduled)
2. Collect input mode:
   - `--message`
   - `--prompt-file`
3. Collect model strategy:
   - single model
   - comma-separated multi-model fan-out
4. Decide output contract:
   - human-readable terminal output
   - machine-readable artifact (`--results`)
5. Confirm secret handling before exporting env vars.

## Critical output distinction (must enforce)

Treat terminal output and `--results` as different products.

- Terminal output (`stdout`):
  - For `--message`, usually the final assistant text printed for humans.
  - For multi-model no target-agent case, formatted display panels/summaries are shown.
- `--results <path>`:
  - Exports **agent message history** from `message_history`.
  - For multi-model runs, writes per-model suffixed files.
  - Use `.json` for machine workflows.

### Mandatory automation rule

For non-trivial automation, always set `--results` and parse that file (prefer JSON). Do not treat raw terminal capture as source-of-truth output.

## Quick patterns

## Model selection policy (important)

Fast-agent resolves models with precedence where an explicit agent model from a card/decorator
outranks CLI `--model`.

- If an agent card sets `model: ...`, that explicit model is used.
- CLI `--model` is best treated as a runtime override only when the selected card agent does not
  set an explicit model.

### Recommended default for automation skills

- Prefer **omitting `model` in automation agent cards** when you want runtime flexibility.
- Pass `--model` in CI/Jobs wrappers so model choice is explicit per run.
- If strict reproducibility is required, pin `model` in the card and document that changing models
  requires card edits.

### Single-shot local

```bash
fast-agent go \
  --card ./cards \
  --agent researcher \
  --model sonnet \
  --message "Summarize findings" \
  --results ./artifacts/run.json
```

### Multi-model compare

```bash
fast-agent go \
  --card ./cards \
  --model "haiku,sonnet" \
  --message "Give a concise plan" \
  --results ./artifacts/compare.json
```

Expect suffixed exports like `compare-haiku.json` and `compare-sonnet.json`.

## Reference map

- CLI options and automation patterns: [references/cli-automation.md](references/cli-automation.md)
- Skills management (`--skills-dir`, card `skills`): [references/skills.md](references/skills.md)
- Docker images and Dockerfile templates: [references/docker.md](references/docker.md)
- Hugging Face Jobs (one-off, scheduled, secrets): [references/hf-jobs.md](references/hf-jobs.md)
- Agent card-first architecture patterns: [references/agent-card-patterns.md](references/agent-card-patterns.md)

## Scripts

- `scripts/run_fast_agent.sh`: local/CI wrapper enforcing `--results`
- `scripts/submit_hf_job.sh`: `hf jobs uv run` helper with explicit secret confirmation
