#!/usr/bin/env bash
set -euo pipefail

# Minimal wrapper for deterministic fast-agent automation.
# Enforces --results to avoid relying on stdout-only capture.

usage() {
  cat <<USAGE
Usage:
  $(basename "$0") [--card <path>] [--agent <name>] [--model <model>] --message <text> --results <file>

Notes:
  - --results is required by this wrapper.
  - Supports both no-card and card-based runs.
  - If --agent is provided, --card is required.
  - Use .json extension for structured artifacts.
USAGE
}

CARD=""
AGENT=""
MODEL=""
MESSAGE=""
RESULTS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --card) CARD="$2"; shift 2 ;;
    --agent) AGENT="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --message) MESSAGE="$2"; shift 2 ;;
    --results) RESULTS="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

[[ -n "$MESSAGE" && -n "$RESULTS" ]] || {
  echo "Missing required arguments" >&2
  usage
  exit 1
}

if [[ -n "$AGENT" && -z "$CARD" ]]; then
  echo "--agent requires --card" >&2
  exit 1
fi

mkdir -p "$(dirname "$RESULTS")"

CMD=(fast-agent go --message "$MESSAGE" --results "$RESULTS")

if [[ -n "$CARD" ]]; then
  CMD+=(--card "$CARD")
fi
if [[ -n "$AGENT" ]]; then
  CMD+=(--agent "$AGENT")
fi
if [[ -n "$MODEL" ]]; then
  CMD+=(--model "$MODEL")
fi

"${CMD[@]}"

echo "Saved results to: $RESULTS"
