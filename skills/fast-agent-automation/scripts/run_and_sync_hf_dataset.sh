#!/usr/bin/env bash
set -euo pipefail

# Reusable end-to-end helper for HF dataset workflows:
# 1) optional prompt download from Hub repo
# 2) run fast-agent with deterministic --results export
# 3) upload result artifact(s) + meta.json under runs/<run-name>/<run-id>/
#
# run-id policy:
# - use JOB_ID when running in Hugging Face Jobs
# - otherwise generate timestamp-pid fallback

usage() {
  cat <<USAGE
Usage:
  $(basename "$0") \
    --repo <owner/repo> \
    --run-name <name> \
    --results <file> \
    [--repo-type dataset|model|space] \
    [--message <text> | --prompt-file <path> | --load-prompt-path <path-in-repo>] \
    [--card <path>] \
    [--agent <name>] \
    [--model <model-or-comma-list>] \
    [--commit-message <text>] \
    [--on-exists error|overwrite|skip] \
    [--summary-json <path>] \
    [--dry-run]

Examples:
  # Message -> run -> upload under runs/<run-name>/<JOB_ID|fallback>/
  $(basename "$0") \
    --repo username/fast-agent-results \
    --run-name nightly-summary \
    --model sonnet \
    --message "nightly summary" \
    --results ./artifacts/run.json

  # Load prompt from repo, then run + upload
  $(basename "$0") \
    --repo username/fast-agent-results \
    --run-name prompt-regression \
    --load-prompt-path prompts/nightly.json \
    --results ./artifacts/nightly.json \
    --model sonnet
USAGE
}

REPO=""
RUN_NAME=""
REPO_TYPE="dataset"
RESULTS=""
MESSAGE=""
PROMPT_FILE=""
LOAD_PROMPT_PATH=""
CARD=""
AGENT=""
MODEL=""
COMMIT_MESSAGE=""
ON_EXISTS="error"
SUMMARY_JSON=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --run-name) RUN_NAME="$2"; shift 2 ;;
    --repo-type) REPO_TYPE="$2"; shift 2 ;;
    --results) RESULTS="$2"; shift 2 ;;
    --message) MESSAGE="$2"; shift 2 ;;
    --prompt-file) PROMPT_FILE="$2"; shift 2 ;;
    --load-prompt-path) LOAD_PROMPT_PATH="$2"; shift 2 ;;
    --card) CARD="$2"; shift 2 ;;
    --agent) AGENT="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --commit-message) COMMIT_MESSAGE="$2"; shift 2 ;;
    --on-exists) ON_EXISTS="$2"; shift 2 ;;
    --summary-json) SUMMARY_JSON="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

[[ -n "$REPO" && -n "$RUN_NAME" && -n "$RESULTS" ]] || {
  echo "Missing required --repo, --run-name, or --results" >&2
  usage
  exit 1
}

case "$REPO_TYPE" in
  dataset|model|space) ;;
  *) echo "Invalid --repo-type: $REPO_TYPE" >&2; exit 1 ;;
esac

case "$ON_EXISTS" in
  error|overwrite|skip) ;;
  *) echo "Invalid --on-exists: $ON_EXISTS (expected error|overwrite|skip)" >&2; exit 1 ;;
esac

if [[ -n "$AGENT" && -z "$CARD" ]]; then
  echo "--agent requires --card" >&2
  exit 1
fi

input_count=0
[[ -n "$MESSAGE" ]] && ((input_count += 1))
[[ -n "$PROMPT_FILE" ]] && ((input_count += 1))
[[ -n "$LOAD_PROMPT_PATH" ]] && ((input_count += 1))
if [[ "$input_count" -ne 1 ]]; then
  echo "Specify exactly one of --message, --prompt-file, or --load-prompt-path" >&2
  exit 1
fi

if ! command -v hf >/dev/null 2>&1; then
  echo "Missing required command: hf" >&2
  echo "Install/enable Hugging Face CLI first." >&2
  exit 1
fi
if ! command -v fast-agent >/dev/null 2>&1; then
  echo "Missing required command: fast-agent" >&2
  exit 1
fi

if [[ -n "$LOAD_PROMPT_PATH" ]]; then
  tmp_prompt_root="${TMPDIR:-/tmp}/fast-agent-prompt-$$"
  mkdir -p "$tmp_prompt_root"
  echo "Downloading prompt from $REPO ($REPO_TYPE): $LOAD_PROMPT_PATH"
  hf download "$REPO" "$LOAD_PROMPT_PATH" \
    --repo-type "$REPO_TYPE" \
    --local-dir "$tmp_prompt_root" >/dev/null

  candidate="$tmp_prompt_root/$LOAD_PROMPT_PATH"
  if [[ -f "$candidate" ]]; then
    PROMPT_FILE="$candidate"
  else
    resolved="$(find "$tmp_prompt_root" -type f | head -n 1 || true)"
    [[ -n "$resolved" ]] || {
      echo "Failed to resolve downloaded prompt file path" >&2
      exit 1
    }
    PROMPT_FILE="$resolved"
  fi
fi

mkdir -p "$(dirname "$RESULTS")"
if [[ -n "$SUMMARY_JSON" ]]; then
  mkdir -p "$(dirname "$SUMMARY_JSON")"
fi

run_cmd=(fast-agent go --results "$RESULTS")
if [[ -n "$MESSAGE" ]]; then
  run_cmd+=(--message "$MESSAGE")
else
  run_cmd+=(--prompt-file "$PROMPT_FILE")
fi
if [[ -n "$CARD" ]]; then
  run_cmd+=(--card "$CARD")
fi
if [[ -n "$AGENT" ]]; then
  run_cmd+=(--agent "$AGENT")
fi
if [[ -n "$MODEL" ]]; then
  run_cmd+=(--model "$MODEL")
fi

run_id="${JOB_ID:-}"
if [[ -z "$run_id" ]]; then
  run_id="$(date -u +%Y%m%dT%H%M%SZ)-$RANDOM-$$"
fi
remote_prefix="runs/${RUN_NAME}/${run_id}"
if [[ -z "$COMMIT_MESSAGE" ]]; then
  COMMIT_MESSAGE="fast-agent run ${RUN_NAME}/${run_id}"
fi

echo "Running command:"
printf '  %q' "${run_cmd[@]}"
printf '\n'
echo "Remote prefix: $REPO ($REPO_TYPE) -> $remote_prefix"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry run enabled; skipping execution and upload."
  exit 0
fi

run_start_epoch="$(date +%s)"
"${run_cmd[@]}"

declare -a result_files=()
declare -A seen=()

add_result_file() {
  local f="$1"
  local mtime
  mtime="$(stat -c %Y "$f" 2>/dev/null || echo 0)"
  if [[ -f "$f" && "$mtime" -ge "$run_start_epoch" && -z "${seen[$f]:-}" ]]; then
    seen["$f"]=1
    result_files+=("$f")
  fi
}

add_result_file "$RESULTS"

result_dir="$(dirname "$RESULTS")"
result_name="$(basename "$RESULTS")"
if [[ "$result_name" == *.* ]]; then
  result_stem="${result_name%.*}"
  result_ext=".${result_name##*.}"
else
  result_stem="$result_name"
  result_ext=""
fi

shopt -s nullglob
if [[ -n "$result_ext" ]]; then
  for f in "$result_dir"/"$result_stem"-*"$result_ext"; do
    add_result_file "$f"
  done
else
  for f in "$result_dir"/"$result_stem"-*; do
    add_result_file "$f"
  done
fi
shopt -u nullglob

if [[ "${#result_files[@]}" -eq 0 ]]; then
  echo "No result files found to upload (expected at least: $RESULTS)" >&2
  exit 1
fi

remote_exists() {
  local remote_path="$1"
  local probe_dir
  probe_dir="$(mktemp -d)"
  if hf download "$REPO" "$remote_path" --repo-type "$REPO_TYPE" --local-dir "$probe_dir" >/dev/null 2>&1; then
    rm -rf "$probe_dir"
    return 0
  fi
  rm -rf "$probe_dir"
  return 1
}

should_upload_path() {
  local remote_path="$1"
  if ! remote_exists "$remote_path"; then
    return 0
  fi

  case "$ON_EXISTS" in
    overwrite)
      echo "Overwriting existing remote file: $remote_path"
      return 0
      ;;
    skip)
      echo "Skipping existing remote file: $remote_path"
      return 1
      ;;
    error)
      echo "Remote file exists and --on-exists=error: $remote_path" >&2
      return 2
      ;;
  esac
}

echo "Uploading ${#result_files[@]} result file(s) to $REPO ($REPO_TYPE)"
declare -a uploaded_remote_paths=()

for local_file in "${result_files[@]}"; do
  remote_path="$remote_prefix/$(basename "$local_file")"

  if ! should_upload_path "$remote_path"; then
    status=$?
    if [[ "$status" -eq 1 ]]; then
      continue
    fi
    exit 1
  fi

  echo "  - $local_file -> $remote_path"
  hf upload "$REPO" "$local_file" "$remote_path" \
    --repo-type "$REPO_TYPE" \
    --commit-message "$COMMIT_MESSAGE" >/dev/null
  uploaded_remote_paths+=("$remote_path")
done

meta_tmp="$(mktemp)"
export META_TMP="$meta_tmp"
export META_RUN_NAME="$RUN_NAME"
export META_RUN_ID="$run_id"
export META_JOB_ID="${JOB_ID:-}"
export META_REPO="$REPO"
export META_REPO_TYPE="$REPO_TYPE"
export META_CARD="$CARD"
export META_AGENT="$AGENT"
export META_MODEL="$MODEL"
export META_RESULTS_LOCAL="$RESULTS"

uploads_tmp="$(mktemp)"
for path in "${uploaded_remote_paths[@]}"; do
  printf '%s\n' "$path" >> "$uploads_tmp"
done
export META_UPLOADS_FILE="$uploads_tmp"

python - <<'PY'
import json
import os
from datetime import datetime, timezone

uploads = []
path = os.environ["META_UPLOADS_FILE"]
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        uploads = [line.strip() for line in f if line.strip()]

doc = {
    "run_name": os.environ["META_RUN_NAME"],
    "run_id": os.environ["META_RUN_ID"],
    "job_id": os.environ.get("META_JOB_ID") or None,
    "repo": os.environ["META_REPO"],
    "repo_type": os.environ["META_REPO_TYPE"],
    "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "card": os.environ.get("META_CARD") or None,
    "agent": os.environ.get("META_AGENT") or None,
    "model": os.environ.get("META_MODEL") or None,
    "results_local": os.environ.get("META_RESULTS_LOCAL") or None,
    "uploaded_files": uploads,
}

with open(os.environ["META_TMP"], "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=2, ensure_ascii=False)
    f.write("\n")
PY

meta_remote="$remote_prefix/meta.json"
if should_upload_path "$meta_remote"; then
  echo "  - $meta_tmp -> $meta_remote"
  hf upload "$REPO" "$meta_tmp" "$meta_remote" \
    --repo-type "$REPO_TYPE" \
    --commit-message "$COMMIT_MESSAGE" >/dev/null
  uploaded_remote_paths+=("$meta_remote")
fi

rm -f "$meta_tmp" "$uploads_tmp"

if [[ -n "$SUMMARY_JSON" ]]; then
  export SUMMARY_JSON_PATH="$SUMMARY_JSON"
  summary_uploads_tmp="$(mktemp)"
  for path in "${uploaded_remote_paths[@]}"; do
    printf '%s\n' "$path" >> "$summary_uploads_tmp"
  done
  export SUMMARY_UPLOADS_FILE="$summary_uploads_tmp"
  export SUMMARY_REPO="$REPO"
  export SUMMARY_REPO_TYPE="$REPO_TYPE"
  export SUMMARY_RUN_NAME="$RUN_NAME"
  export SUMMARY_RUN_ID="$run_id"
  export SUMMARY_JOB_ID="${JOB_ID:-}"
  export SUMMARY_REMOTE_PREFIX="$remote_prefix"

  python - <<'PY'
import json
import os
from datetime import datetime, timezone

uploads = []
path = os.environ["SUMMARY_UPLOADS_FILE"]
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        uploads = [line.strip() for line in f if line.strip()]

summary = {
    "ok": True,
    "repo": os.environ["SUMMARY_REPO"],
    "repo_type": os.environ["SUMMARY_REPO_TYPE"],
    "run_name": os.environ["SUMMARY_RUN_NAME"],
    "run_id": os.environ["SUMMARY_RUN_ID"],
    "job_id": os.environ.get("SUMMARY_JOB_ID") or None,
    "remote_prefix": os.environ["SUMMARY_REMOTE_PREFIX"],
    "uploaded_files": uploads,
    "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
with open(os.environ["SUMMARY_JSON_PATH"], "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
    f.write("\n")
PY

  rm -f "$summary_uploads_tmp"
fi

echo "Done. Uploaded artifact(s) to $REPO/$remote_prefix"
