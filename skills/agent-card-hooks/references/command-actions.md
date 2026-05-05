# Command actions API

Command actions are user-invoked fast-agent add-ins. They are configured with
`commands:` and invoked as slash commands. Optional keybindings are a TUI-only
shortcut for the same slash command path.

Use command actions for explicit user operations. Use hooks for automatic
lifecycle/turn behavior.

## Configuration

### Global commands

In the resolved `fast-agent.yaml`:

```yaml
commands:
  draft-next:
    description: Draft the next user message
    input_hint: "[format]"
    handler: "./command-actions.py:draft_next"
    key: "c-x d"
```

Global relative `handler` paths resolve from the directory containing the
resolved `fast-agent.yaml`.

### AgentCard commands

In AgentCard frontmatter:

```yaml
---
type: smart
name: dev
commands:
  review-last:
    description: Ask a reviewer agent to review the latest assistant response
    input_hint: "[agent-name]"
    handler: "./commands.py:review_last"
    key: "c-x r"
---
```

AgentCard relative `handler` paths resolve from the AgentCard directory.

### Metadata fields

| Field | Required | Meaning |
| --- | --- | --- |
| `description` | yes | Human-facing summary for discovery/completion |
| `handler` | yes | Async Python callable in `path.py:function` format |
| `input_hint` | no | Argument hint shown to users |
| `key` | no | Prompt-toolkit key sequence for TUI |

## Resolution order

1. Built-in slash commands
2. Current agent command actions
3. Global command actions
4. Unknown command

Built-ins cannot be shadowed. Agent commands override global commands with the
same name.

## Handler signature

```python
from fast_agent.command_actions import PluginCommandActionContext


async def my_command(ctx: PluginCommandActionContext):
    ...
```

Handlers may return:

- `PluginCommandActionResult`
- `str` (`message=value`)
- `None` (empty successful result)

## `PluginCommandActionContext`

Common fields and helpers:

```python
ctx.command_name       # command name without leading slash
ctx.arguments          # raw argument string
ctx.agent              # current agent
ctx.agent_name         # current agent name
ctx.message_history    # current agent history
ctx.context            # application context, if available
ctx.settings           # Settings object, if available
ctx.session_cwd        # workspace/session cwd, if available

ctx.load_message_history(messages)
ctx.get_agent("critic")
ctx.mark_user_adjusted(message, note="...")
```

`ctx.get_agent(name)` looks up another configured agent. Calling `send()` on
that agent uses the agent normally and may update that agent's history.

## `PluginCommandActionResult`

```python
from fast_agent.command_actions import PluginCommandActionResult

return PluginCommandActionResult(
    message="Done.",
    markdown=None,
    buffer_prefill="Proposed next user message",
    switch_agent=None,
    refresh_agents=False,
)
```

| Field | Meaning |
| --- | --- |
| `message` | Plain status text |
| `markdown` | Markdown output; preferred over `message` when set |
| `buffer_prefill` | Replace TUI input buffer; never auto-submit |
| `switch_agent` | Switch to an agent after command execution |
| `refresh_agents` | Refresh/reload available agents |

There is intentionally no auto-submit field. Drafted user messages should be
returned as `buffer_prefill` so the user can review or edit them.

## Keybindings

`key` uses prompt-toolkit notation:

| Key string | Meaning |
| --- | --- |
| `c-x d` | Ctrl-X, then D |
| `c-x c-e` | Ctrl-X, then Ctrl-E |
| `f6` | F6 |
| `escape` | Escape |

Invalid keybindings are ignored with a warning log.

## Examples

### Draft next user message

```python
from fast_agent.command_actions import (
    PluginCommandActionContext,
    PluginCommandActionResult,
)


async def draft_next(ctx: PluginCommandActionContext) -> PluginCommandActionResult:
    drafter = ctx.get_agent("drafter") or ctx.agent
    style = ctx.arguments.strip() or "concise"

    draft = await drafter.send(
        "Draft the next user message based on the current conversation. "
        f"Use this format: {style}. "
        "Return only the proposed user message."
    )

    return PluginCommandActionResult(
        message="Drafted the next user message.",
        buffer_prefill=draft.strip(),
    )
```

### Review recent context with another agent

```python
from fast_agent.command_actions import (
    PluginCommandActionContext,
    PluginCommandActionResult,
)


async def review_last(ctx: PluginCommandActionContext) -> PluginCommandActionResult:
    reviewer_name = ctx.arguments.strip() or "critic"
    reviewer = ctx.get_agent(reviewer_name)
    if reviewer is None:
        return PluginCommandActionResult(
            message=f"No agent named {reviewer_name!r} is configured."
        )

    review = await reviewer.send(
        "Review the latest assistant response in the active conversation. "
        "Focus on correctness, safety, missing edge cases, and concrete next steps. "
        "Be concise."
    )

    return PluginCommandActionResult(
        markdown=f"## Review from `{reviewer_name}`\n\n{review.strip()}"
    )
```

### Edit last assistant text into the input buffer

```python
import asyncio
import os
import shlex
import subprocess
import tempfile
from pathlib import Path

from fast_agent.command_actions import (
    PluginCommandActionContext,
    PluginCommandActionResult,
)


async def editlast(ctx: PluginCommandActionContext) -> PluginCommandActionResult:
    """Open the last assistant message in $VISUAL/$EDITOR and prefill edits."""
    for message in reversed(ctx.message_history):
        if message.role != "assistant" or (original := message.last_text()) is None:
            continue

        try:
            edited, saved = await asyncio.to_thread(
                _edit_text,
                original,
                cwd=ctx.session_cwd,
            )
        except subprocess.CalledProcessError as exc:
            return PluginCommandActionResult(
                message=f"Editor exited with status {exc.returncode}."
            )
        except (OSError, UnicodeError, ValueError) as exc:
            return PluginCommandActionResult(message=f"Editor failed: {exc}")

        if edited == original:
            return PluginCommandActionResult(
                message=(
                    "Editor saved without changing the message."
                    if saved
                    else "No saved editor changes detected."
                )
            )

        return PluginCommandActionResult(
            message="Edited last assistant message; review before sending.",
            buffer_prefill=edited,
        )

    return PluginCommandActionResult(message="No assistant text found.")


def _edit_text(initial_text: str, *, cwd: Path | None = None) -> tuple[str, bool]:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        temp_path = Path(temp_dir, "message.md")
        temp_path.write_text(initial_text, encoding="utf-8")
        before_mtime = temp_path.stat().st_mtime_ns
        subprocess.run([*_editor_args(), str(temp_path)], cwd=cwd, check=True)
        after_mtime = temp_path.stat().st_mtime_ns
        return temp_path.read_text(encoding="utf-8"), after_mtime != before_mtime


def _editor_args() -> list[str]:
    editor_cmd = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    editor_args = shlex.split(editor_cmd or _default_editor(), posix=os.name != "nt")
    if not editor_args:
        raise ValueError("editor command is empty")
    return editor_args


def _default_editor() -> str:
    return "notepad" if os.name == "nt" else "nano"
```

This command intentionally returns `buffer_prefill` instead of mutating history:
the user gets a reviewable draft in the input buffer. If a command does mutate
history, use `ctx.mark_user_adjusted(...)` with `ctx.load_message_history(...)`
to preserve provenance.

## Source-of-truth files

| Area | Source |
| --- | --- |
| Command action models | `src/fast_agent/command_actions/models.py` |
| Loader | `src/fast_agent/command_actions/loader.py` |
| Registry | `src/fast_agent/command_actions/registry.py` |
| AgentCard parsing | `src/fast_agent/core/agent_card_loader.py` |
| TUI dispatch | `src/fast_agent/ui/interactive/command_dispatch.py` |
| TUI keybindings | `src/fast_agent/ui/prompt/keybindings.py` |
