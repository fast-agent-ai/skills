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
2. Choose execution mode:
   - default agent/instruction (no card)
   - card-driven (`--card`, optional `--agent`)
3. Collect input mode:
   - `--message`
   - `--prompt-file`
4. Collect model strategy:
   - single model
   - comma-separated multi-model fan-out
5. Decide output contract:
   - human-readable terminal output
   - machine-readable artifact (`--results`)
   - machine-readable stdout contract (`--json-schema` for one-shot runs)
   - Hugging Face Job artifact persistence plan (upload from within the job when needed)
   - Prefer script-based dataset sync for pre-run download and post-run publishing
6. Confirm secret handling before exporting env vars.
7. Use `fast-agent check models --for-model ... --json` to precompute candidate secret env var names when model(s) are known.

### IMPORTANT SECURITY RULE

Never relay raw secret values in prompts or CLI args.
Only relay environment-variable **names** (for example `OPENAI_API_KEY`) through approved secret
channels/stores.

For Hugging Face Jobs specifically, prefer `--secrets NAME` (for example `--secrets OPENAI_API_KEY`).

## Hugging Face Jobs pitfalls to encode in generated guidance

When proposing or generating HF Job commands, include these operational guardrails:

- Use `fast-agent check models --for-model "<model>" --json` first and forward only discovered secret **names**.
- If the job command itself runs `hf ...` subcommands (for example `hf upload`), include `--with huggingface-hub`.
- Job files are ephemeral inside the container; recommend uploading artifacts from inside the job to persistent storage.
- For multi-step in-job flows, prefer `-- bash -c "cmd1 && cmd2"`.
- Avoid long inline `python -c` blobs in `hf jobs uv run` commands; use `bash -c` or a checked-in script file.
- Include job lifecycle commands in runbooks (`hf jobs ps`, `inspect`, `logs`, `cancel`, `hardware`).

## Execution mode guidance

Default agent/instruction (no card) is usually enough for:

- smoke tests
- one-off prompts
- simple scheduled jobs without custom orchestration

Use an agent card when you need custom system prompts/instructions or runtime config, such as:

- card-defined instruction and behavior
- MCP server setup/allowlists
- skill selection and `skills: []` control
- child agents / workflow composition
- pinned request params or model defaults

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

### Exception: strict one-shot JSON stdout

When the caller explicitly needs a single validated JSON document on stdout, use:

- `fast-agent go --no-env --message ... --json-schema schema.json`
- or `fast-agent go --no-env --prompt-file ... --json-schema schema.json`

In this mode:

- stdout is the source of truth
- local schema validation is enforced before emission
- multi-model fan-out is intentionally unsupported

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

Default agent/instruction (no card):

```bash
fast-agent go \
  --noenv \
  --model sonnet \
  --message "Summarize findings" \
  --results ./artifacts/run.json
```

Card-based run:

```bash
fast-agent go \
  --no-env \
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

### Structured stdout recipe

```bash
fast-agent go \
  --no-env \
  --card ./cards \
  --agent researcher \
  --model sonnet \
  --message "What is the weather in London?" \
  --json-schema ./schema.json
```

## Reference map

- CLI options and automation patterns: [references/cli-automation.md](references/cli-automation.md)
- Skills management (`--skills-dir`, card `skills`): [references/skills.md](references/skills.md)
- Docker images and Dockerfile templates: [references/docker.md](references/docker.md)
- Hugging Face Jobs (one-off, scheduled, secrets): [references/hf-jobs.md](references/hf-jobs.md)
- Hugging Face Dataset load/save wrapper patterns: [references/hf-dataset-sync.md](references/hf-dataset-sync.md)
- Agent card-first architecture patterns: [references/agent-card-patterns.md](references/agent-card-patterns.md)

## Scripts

- `scripts/run_fast_agent.sh`: local/CI wrapper enforcing `--results` (supports both no-card and card-based runs)
- `scripts/submit_hf_job.sh`: `hf jobs uv run` helper with explicit secret confirmation (supports both no-card and card-based runs)
- `scripts/run_and_sync_hf_dataset.sh`: reusable v2 wrapper for optional prompt download + `fast-agent go --results` + dataset upload under `runs/<run-name>/<JOB_ID|generated-id>/`
