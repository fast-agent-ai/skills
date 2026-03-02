# HF Dataset Load/Save Wrapper (v2)

Use `scripts/run_and_sync_hf_dataset.sh` for a reusable one-shot workflow that:

1. optionally downloads prompt/input content from Hub,
2. runs `fast-agent go` with required `--results`,
3. uploads produced run artifacts to dataset/model/space repos.

Keep this in the automation layer (skill script), not in fast-agent core.

> Path note: examples use a path relative to the skill folder (`scripts/...`). If running from a
> repo root, prefix accordingly (for example `skills/fast-agent-automation/scripts/...`).

---

## Why use this wrapper

- Enforce `--results` as source-of-truth artifact contract.
- Reuse one contract across local, CI, and HF Jobs.
- Support pre-run data pull + post-run data push.
- Produce stable remote paths for run discoverability.

---

## v2 contract

### Required flags

- `--repo <owner/name>`
- `--run-name <name>`
- `--results <file>`

### Input mode (exactly one)

- `--message <text>`
- `--prompt-file <local-file>`
- `--load-prompt-path <path-in-repo>`

### Optional flags

- `--repo-type dataset|model|space` (default `dataset`)
- `--card <path>`
- `--agent <name>` (requires `--card`)
- `--model <model-or-comma-list>`
- `--commit-message <text>`
- `--on-exists error|overwrite|skip` (default `error`)
- `--summary-json <path>`
- `--dry-run`

---

## Run identity and remote path

Use built-in HF Jobs env var `JOB_ID` when present.

- If `JOB_ID` exists, set `run_id = JOB_ID`.
- Else, generate `run_id` locally (timestamp + short UUID).

Remote prefix:

- `runs/<run-name>/<run_id>/`

Examples:

- `runs/nightly-summary/699d874f1aad19adb8aaeadc/result.json`
- `runs/nightly-summary/699d874f1aad19adb8aaeadc/result-sonnet.json`
- `runs/nightly-summary/699d874f1aad19adb8aaeadc/meta.json`

---

## Metadata sidecar

Write `meta.json` alongside uploaded artifacts.

Minimal fields:

```json
{
  "run_name": "nightly-summary",
  "run_id": "699d874f1aad19adb8aaeadc",
  "job_id": "699d874f1aad19adb8aaeadc",
  "repo": "username/fast-agent-results",
  "repo_type": "dataset",
  "created_at_utc": "2026-03-02T20:15:10Z",
  "card": "./cards",
  "agent": "automation",
  "model": "haiku,sonnet",
  "results_local": "./artifacts/compare.json",
  "uploaded_files": [
    "runs/nightly-summary/699.../compare-haiku.json",
    "runs/nightly-summary/699.../compare-sonnet.json",
    "runs/nightly-summary/699.../meta.json"
  ]
}
```

---

## Behavioral rules

- Enforce exactly one input mode.
- Require `--card` when `--agent` is provided.
- Fail if no output file exists at `--results` after run.
- Detect and upload fan-out result files (suffixed outputs).
- Return non-zero on any download/run/upload failure.
- Honor `--dry-run` by printing planned commands and remote paths only.

---

## HF Jobs usage

When used in `hf jobs uv run`, include:

- `--with fast-agent-mcp`
- `--with huggingface-hub` (script uses `hf download` / `hf upload`)
- `--secrets HF_TOKEN` + model provider secrets

Example:

```bash
hf jobs uv run \
  --python 3.13 \
  --with fast-agent-mcp \
  --with huggingface-hub \
  --secrets HF_TOKEN \
  --secrets ANTHROPIC_API_KEY \
  -- bash -lc '
    ./skills/fast-agent-automation/scripts/run_and_sync_hf_dataset.sh \
      --repo username/fast-agent-results \
      --run-name nightly-summary \
      --model sonnet \
      --message "nightly summary" \
      --results result.json
  '
```

---

## Security reminders

- Never pass raw secret values via command args.
- Pass secret **names** only (`--secrets HF_TOKEN`).
- Let CI/HF secret stores provide runtime values.
