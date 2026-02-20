#!/usr/bin/env bash
set -euo pipefail

# Minimal wrapper for deterministic fast-agent automation.
# Enforces --results to avoid relying on stdout-only capture.

usage() {
  cat <<USAGE
Usage:
  $(basename "$0") --card <path> --agent <name> --model <model> --message <text> --results <file>

Notes:
  - --results is required by this wrapper.
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

[[ -n "$CARD" && -n "$AGENT" && -n "$MODEL" && -n "$MESSAGE" && -n "$RESULTS" ]] || {
  echo "Missing required arguments" >&2
  usage
  exit 1
}

mkdir -p "$(dirname "$RESULTS")"

fast-agent go \
  --card "$CARD" \
  --agent "$AGENT" \
  --model "$MODEL" \
  --message "$MESSAGE" \
  --results "$RESULTS"

echo "Saved results to: $RESULTS"
