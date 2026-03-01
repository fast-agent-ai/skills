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

## Model → secret planning helper

Use fast-agent to resolve model(s) to candidate secret env var names before job submission:

```bash
fast-agent check models --for-model "sonnet,kimi" --json
```

Read `candidate_secret_env_vars` from output and pass those *names* only via `--secrets`.

## Secret safety policy

Before submitting Jobs, enumerate candidate env vars and ask user confirmation.
Never silently forward local secrets.

HF CLI accepts secrets in two forms:

- `--secrets NAME` (name-only; preferred for automation guidance/transcripts)
- `--secrets NAME=value` (allowed by HF CLI, but avoid inline values in shared logs/transcripts)

For this skill, prefer **name-only** usage so secret values are handled by secure storage/routing,
not pasted into command strings.

**IMPORTANT:** Never pass raw secret values in CLI arguments.
Only pass environment variable names (for example `--secrets OPENAI_API_KEY`) and rely on secure
secret stores/routes (HF Secrets, CI secrets, key vaults) for the actual values.

### Simple demonstration

Safe (name-only):

```bash
hf jobs uv run \
  --with fast-agent-mcp \
  --secrets OPENAI_API_KEY \
  -- fast-agent go --model responses.gpt-5-mini --message "hi" --results result.json
```

Not allowed in this skill guidance (raw value visible):

```bash
hf jobs uv run ... --secrets OPENAI_API_KEY=sk_live_abc123
```

Suggested candidate list:

- `HF_TOKEN`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- provider-specific model keys requested by the user

## In-job artifact handling (important)

Artifacts created by `fast-agent go --results ...` live inside the Job container filesystem.
They are **not** automatically downloaded to your local machine after completion.

### Recommended: upload in the same job

If you need durable artifacts, upload from inside the job to a Dataset/Model/Space repo.

```bash
hf jobs uv run \
  --python 3.13 \
  --with fast-agent-mcp \
  --with huggingface-hub \
  --flavor cpu-basic \
  --timeout 20m \
  --secrets ANTHROPIC_API_KEY \
  --secrets HF_TOKEN \
  -- bash -c "
    fast-agent go --model sonnet --message 'nightly summary' --results result.json &&
    hf upload username/fast-agent-results ./result.json result.json --repo-type=dataset
  "
```

### Alternative: inspect job outputs/logs

```bash
hf jobs inspect <job_id>
hf jobs logs <job_id>
```

## Command chaining patterns

For multi-step job commands, prefer shell chaining via `bash -c`:

```bash
hf jobs uv run \
  --with fast-agent-mcp \
  --with huggingface-hub \
  -- bash -c "fast-agent go --results result.json && hf upload ..."
```

Avoid long inline `python -c` scripts in job submission commands. Use short snippets only, or
store logic in a checked-in script file.

## Job management quick reference

```bash
hf jobs ps
hf jobs inspect <job_id>
hf jobs logs <job_id>
hf jobs cancel <job_id>
hf jobs hardware
```

## Dataset upload quick reference

```bash
# Upload to a dataset repo
hf upload username/dataset-name ./local-file.json remote-path.json --repo-type=dataset

# Upload to a model repo (default)
hf upload username/model-name ./file.safetensors file.safetensors

# Create PR instead of direct commit
hf upload username/repo ./file . --create-pr
```

## MCP alternative

Hugging Face MCP server includes job-management tools. Prefer CLI examples first for reproducibility unless user specifically requests MCP-invoked job control.
