#!/usr/bin/env bash
set -euo pipefail

# Submit a Hugging Face Job that runs fast-agent with explicit secret confirmation.

usage() {
  cat <<USAGE
Usage:
  $(basename "$0") \
    [--card <path>] \
    [--agent <name>] \
    [--model <model>] \
    --message <text> \
    [--schedule <cron-or-alias>] \
    [--flavor <hf-flavor>] \
    [--timeout <duration>] \
    [--secrets HF_TOKEN,OPENAI_API_KEY]

Examples:
  $(basename "$0") --model kimi --message "smoke test" \
    --secrets HF_TOKEN,OPENROUTER_API_KEY

  $(basename "$0") --card cards --agent automation --model sonnet --message "nightly" \
    --secrets HF_TOKEN,OPENAI_API_KEY

  $(basename "$0") --card cards --agent automation --model sonnet --message "hourly" \
    --schedule @hourly --secrets HF_TOKEN
USAGE
}

CARD=""
AGENT=""
MODEL=""
MESSAGE=""
SCHEDULE=""
FLAVOR="cpu-basic"
TIMEOUT="2h"
SECRETS="HF_TOKEN"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --card) CARD="$2"; shift 2 ;;
    --agent) AGENT="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --message) MESSAGE="$2"; shift 2 ;;
    --schedule) SCHEDULE="$2"; shift 2 ;;
    --flavor) FLAVOR="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --secrets) SECRETS="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

[[ -n "$MESSAGE" ]] || {
  echo "Missing required arguments" >&2
  usage
  exit 1
}

if [[ -n "$AGENT" && -z "$CARD" ]]; then
  echo "--agent requires --card" >&2
  exit 1
fi

IFS=',' read -r -a SECRET_KEYS <<< "$SECRETS"

echo "Candidate secrets to forward:"
FORWARD_FLAGS=()
for key in "${SECRET_KEYS[@]}"; do
  key_trimmed="$(echo "$key" | xargs)"
  [[ -n "$key_trimmed" ]] || continue
  if [[ -n "${!key_trimmed:-}" ]]; then
    echo "  - $key_trimmed (present)"
  else
    echo "  - $key_trimmed (NOT set locally)"
  fi
  FORWARD_FLAGS+=("--secrets" "$key_trimmed")
done

read -r -p "Proceed and forward these as HF job secrets? [y/N] " confirm
[[ "$confirm" =~ ^[Yy]$ ]] || { echo "Cancelled"; exit 1; }

COMMON_ARGS=(
  --python 3.13
  --with fast-agent-mcp
  --flavor "$FLAVOR"
  --timeout "$TIMEOUT"
  "${FORWARD_FLAGS[@]}"
  --
  fast-agent go
  --message "$MESSAGE"
  --results result.json
)

if [[ -n "$CARD" ]]; then
  COMMON_ARGS+=(--card "$CARD")
fi
if [[ -n "$AGENT" ]]; then
  COMMON_ARGS+=(--agent "$AGENT")
fi
if [[ -n "$MODEL" ]]; then
  COMMON_ARGS+=(--model "$MODEL")
fi

if [[ -n "$SCHEDULE" ]]; then
  hf jobs scheduled uv run "$SCHEDULE" "${COMMON_ARGS[@]}"
else
  hf jobs uv run "${COMMON_ARGS[@]}"
fi
