---
name: session-investigator
description: Investigate fast-agent session and history files to diagnose issues. Use when a session ended unexpectedly, when debugging tool loops, when correlating sub-agent traces with main sessions, or when analyzing conversation flow and timing. Covers session.json metadata, history JSON format, message structure, tool call/result correlation, and common failure patterns.
---

# Session Investigator

Diagnose fast-agent session issues by examining session and history files.

## Session Directory Structure

Sessions are stored in a client-specific session root, commonly:

- `.fast-agent/sessions/<session-id>/`
- `.cdx/sessions/<session-id>/`

Typical layout:

```
2601181023-Kob2h3/
├── session.json              # Session metadata
├── history_<agent>.json      # Current agent history
└── history_<agent>_previous.json  # Previous save (rotation backup)
```

Session IDs encode creation time: `YYMMDDHHMM-<random>` (e.g., `2601181023` = 2026-01-18 10:23).

## Key Files

### session.json

There are now two formats in the wild:

#### Current v2 snapshot format

```json
{
  "schema_version": 2,
  "session_id": "2601181023-Kob2h3",
  "created_at": "2026-01-18T10:23:24.116526",
  "last_activity": "2026-01-18T10:39:42.873467",
  "metadata": {
    "title": null,
    "label": null,
    "first_user_preview": "is it possible to override...",
    "pinned": false,
    "extras": {
      "model": "$system.default"
    }
  },
  "continuation": {
    "active_agent": "dev",
    "cwd": null,
    "lineage": {
      "forked_from": null,
      "acp_session_id": null
    },
    "agents": {
      "dev": {
        "history_file": "history_dev.json",
        "resolved_prompt": "...",
        "model": "gpt-5.4",
        "provider": "codexresponses",
        "request_settings": {
          "use_history": true,
          "parallel_tool_calls": true
        },
        "card_provenance": [{"ref": "/abs/path/to/card.md"}],
        "attachment_refs": [],
        "model_overlay_refs": []
      }
    }
  },
  "analysis": {
    "usage_summary": {
      "input_tokens": 1234,
      "output_tokens": 56,
      "total_tokens": 1290
    },
    "timing_summary": null,
    "provider_diagnostics": [],
    "transport_diagnostics": []
  }
}
```

Key v2 fields:

- `schema_version: 2` marks the typed snapshot format.
- `session_id` replaces legacy `name`.
- `continuation.active_agent` replaces legacy `metadata.agent_name`.
- `continuation.agents.<agent>.history_file` replaces legacy top-level `history_files` as the authoritative per-agent mapping.
- `analysis.usage_summary` is persisted inspection data, not live runtime truth.

#### Legacy unversioned format

Older sessions may still use:

```json
{
  "name": "2601181023-Kob2h3",
  "created_at": "2026-01-18T10:23:24.116526",
  "last_activity": "2026-01-18T10:39:42.873467",
  "history_files": ["history_dev_previous.json", "history_dev.json"],
  "metadata": {
    "agent_name": "dev",
    "first_user_preview": "is it possible to override..."
  }
}
```

### history\_<agent>.json

```json
{
  "messages": [
    {
      "role": "user|assistant",
      "content": [{"type": "text", "text": "..."}],
      "tool_calls": {"<id>": {"method": "tools/call", "params": {"name": "...", "arguments": {}}}},
      "tool_results": {"<id>": {"content": [...], "isError": false}},
      "channels": {
        "fast-agent-timing": [{"type": "text", "text": "{\"start_time\": ..., \"end_time\": ..., \"duration_ms\": ...}"}],
        "fast-agent-tool-timing": [{"type": "text", "text": "{\"<tool_id>\": {\"timing_ms\": ..., \"transport_channel\": ...}}"}],
        "reasoning": [{"type": "text", "text": "..."}]
      },
      "stop_reason": "endTurn|toolUse|error",
      "is_template": false
    }
  ]
}
```

## Investigation Commands

### Basic inspection

```bash
# Detect session format / top-level keys
jq '{schema_version, session_id: (.session_id // .name), top_level_keys: keys}' session.json

# Show session headline fields for either legacy or v2
jq '{
  session_id: (.session_id // .name),
  created_at,
  last_activity,
  pinned: (.metadata.pinned // false),
  title: (.metadata.title // .metadata.label // .metadata.first_user_preview // null),
  active_agent: (.continuation.active_agent // .metadata.agent_name // null)
}' session.json

# List per-agent history files for either legacy or v2
jq 'if .schema_version == 2 then
      (.continuation.agents // {} | to_entries | map({
        agent: .key,
        history_file: .value.history_file,
        model: .value.model,
        provider: .value.provider
      }))
    else
      ((.metadata.last_history_by_agent // {}) | to_entries | map({
        agent: .key,
        history_file: .value
      }))
    end' session.json

# Show persisted analysis/usage summary when present
jq '.analysis // {}' session.json

# Message count
jq '.messages | length' history_dev.json

# Last N messages overview
jq '.messages[-5:] | .[] | {role, stop_reason, has_tool_calls: (.tool_calls != null), has_tool_results: (.tool_results != null)}' history_dev.json

# View specific message
jq '.messages[227]' history_dev.json
```

### Tool call correlation

Tool calls and results are linked by correlation ID. Valid pattern: assistant with `tool_calls` → user with matching `tool_results`.

```bash
# Check tool call/result pairing
jq '.messages[-10:] | to_entries | .[] | {
  index: .key,
  role: .value.role,
  tool_calls: (if .value.tool_calls then (.value.tool_calls | keys) else [] end),
  tool_results: (if .value.tool_results then (.value.tool_results | keys) else [] end)
}' history_dev.json
```

### Find specific tool calls

```bash
# Find all calls to a specific tool
jq '.messages | to_entries | .[] |
  select(.value.tool_calls != null) |
  select(.value.tool_calls | to_entries | .[0].value.params.name == "agent__ripgrep_search") |
  {index: .key, timing: (.value.channels."fast-agent-timing"[0].text)}' history_dev.json
```

## Session Statistics

### Session Snapshot Stats

```bash
# Persisted token summary from v2 session snapshot
jq '.analysis.usage_summary // null' session.json

# Rich per-agent continuation summary from v2 snapshot
jq 'if .schema_version == 2 then
      .continuation.agents | to_entries | map({
        agent: .key,
        history_file: .value.history_file,
        model: .value.model,
        provider: .value.provider,
        has_prompt: (.value.resolved_prompt != null),
        attachment_refs: (.value.attachment_refs | map(.ref)),
        overlays: (.value.model_overlay_refs | map(.ref))
      })
    else
      "legacy-session"
    end' session.json
```

### LLM Call Stats

```bash
# Total LLM time and call count
jq '[.messages[] | select(.role == "assistant") |
  select(.channels."fast-agent-timing") |
  .channels."fast-agent-timing"[0].text | fromjson | .duration_ms] |
  {count: length, total_ms: add, avg_ms: (add/length), max_ms: max, min_ms: min}' history_dev.json

# LLM calls sorted by duration (slowest first)
jq '[.messages | to_entries | .[] |
  select(.value.role == "assistant") |
  select(.value.channels."fast-agent-timing") |
  {index: .key, duration_ms: (.value.channels."fast-agent-timing"[0].text | fromjson | .duration_ms)}] |
  sort_by(-.duration_ms) | .[0:10]' history_dev.json
```

### Tool Execution Stats

```bash
# All tool timings aggregated
jq '[.messages[] | select(.channels."fast-agent-tool-timing") |
  .channels."fast-agent-tool-timing"[0].text | fromjson | to_entries | .[].value.timing_ms] |
  {count: length, total_ms: add, avg_ms: (add/length), max_ms: max, min_ms: min}' history_dev.json

# Tool calls by name with timing
jq '[.messages | to_entries | .[] |
  select(.value.tool_calls) |
  (.value.tool_calls | to_entries | .[0]) as $tc |
  {index: .key, tool: $tc.value.params.name,
   llm_ms: (.value.channels."fast-agent-timing"[0].text | fromjson | .duration_ms)}] |
  group_by(.tool) |
  map({tool: .[0].tool, count: length, total_llm_ms: (map(.llm_ms) | add)}) |
  sort_by(-.count)' history_dev.json
```

### Session Timeline

```bash
# Session duration from first to last timing
jq '.messages | [
  (map(select(.channels."fast-agent-timing")) | first | .channels."fast-agent-timing"[0].text | fromjson | .start_time),
  (map(select(.channels."fast-agent-timing")) | last | .channels."fast-agent-timing"[0].text | fromjson | .end_time)
] | {start: .[0], end: .[1], duration_sec: ((.[1] - .[0]) | round)}' history_dev.json

# Message rate over time (messages per minute estimate)
jq '{
  messages: (.messages | length),
  llm_calls: [.messages[] | select(.role == "assistant" and .channels."fast-agent-timing")] | length,
  total_llm_ms: [.messages[] | select(.channels."fast-agent-timing") | .channels."fast-agent-timing"[0].text | fromjson | .duration_ms] | add,
  total_tool_ms: [.messages[] | select(.channels."fast-agent-tool-timing") | .channels."fast-agent-tool-timing"[0].text | fromjson | to_entries | .[].value.timing_ms] | add
} | . + {llm_sec: (.total_llm_ms/1000), tool_sec: ((.total_tool_ms//0)/1000)}' history_dev.json
```

### Sub-agent Stats

```bash
# Sub-agent calls (tools starting with "agent__")
jq '[.messages | to_entries | .[] |
  select(.value.tool_calls) |
  (.value.tool_calls | to_entries | .[0]) as $tc |
  select($tc.value.params.name | startswith("agent__")) |
  {index: .key, agent: $tc.value.params.name,
   llm_ms: (.value.channels."fast-agent-timing"[0].text | fromjson | .duration_ms)}] |
  group_by(.agent) |
  map({agent: .[0].agent, calls: length, total_ms: (map(.llm_ms) | add), avg_ms: ((map(.llm_ms) | add) / length)})' history_dev.json
```

## Common Failure Patterns

### Unanswered Tool Call

**Symptom**: API error "No tool output found for function call"

**Pattern**: History ends with `assistant` message having `tool_calls` and `stop_reason: "toolUse"`, followed by `user` message WITHOUT matching `tool_results`.

```bash
# Check last message for pending tool call
jq '.messages[-1] | {role, has_tool_calls: (.tool_calls != null), stop_reason}' history_dev.json
```

**Cause**: Session interrupted mid-tool-loop, then resumed with new user input before tool completed.

When working with v2 snapshots, you usually fix the relevant `history_<agent>.json`, not `session.json`. The snapshot just points at the history file via `continuation.agents.<agent>.history_file`.

**Fix**: Truncate history to last valid tool result:

```bash
# Find last user message with tool_results
jq '.messages | to_entries | map(select(.value.role == "user" and .value.tool_results != null)) | last | .key' history_dev.json

# Truncate (keep messages 0 to N inclusive, so use N+1)
jq '.messages = .messages[0:227]' history_dev.json > /tmp/fixed.json && mv /tmp/fixed.json history_dev.json
```

### Duplicate User Messages

**Pattern**: Two consecutive `user` messages before assistant response.

**Cause**: Often from `before_llm_call` hooks appending instructions. Check agent card's `tool_hooks` configuration.

### Missing or mismatched resumed agent

**Pattern**: Resumed session loads, but the expected active agent is unavailable or different.

Inspect:

```bash
# v2 active agent + known persisted agents
jq '{
  active_agent: (.continuation.active_agent // .metadata.agent_name // null),
  persisted_agents: (
    if .schema_version == 2
    then (.continuation.agents | keys)
    else ((.metadata.last_history_by_agent // {}) | keys)
    end
  )
}' session.json
```

If a persisted agent exists in `session.json` but is missing from the current runtime, expect resume warnings about a missing agent and partial hydration.

## Sub-agent Trace Correlation

Sub-agent traces are saved as `<agent_name>-<timestamp>.json` in the working directory.

```bash
# List traces around session time
ls -la ripgrep_search*2026-01-18-10-3*.json

# Correlate via timing - match monotonic clock values
jq '.messages[-1].channels."fast-agent-timing"[0].text' ripgrep_search*.json
```

Compare `start_time`/`end_time` values between main session and sub-agent traces to correlate which sub-agent call corresponds to which main session tool call.

## Log File

Check `fastagent.jsonl` for errors during the session timeframe:

```bash
# Filter by timestamp range
cat fastagent.jsonl | while read line; do
  ts=$(echo "$line" | jq -r '.timestamp // empty' 2>/dev/null)
  if [[ "$ts" > "2026-01-18T10:20" && "$ts" < "2026-01-18T10:45" ]]; then
    echo "$line" | jq -c '{timestamp, level, message}'
  fi
done
```

## Practical Notes

- Prefer inspecting `session.json` first to identify the active agent and the authoritative history file path.
- For v2 sessions, treat `continuation.agents` as the source of truth for per-agent state.
- For legacy sessions, expect only coarse metadata plus `history_files` / `metadata.last_history_by_agent`.
- `analysis` data in v2 is helpful for inspection, but resumed runtime state may be rebuilt from history rather than copied verbatim from the snapshot.
