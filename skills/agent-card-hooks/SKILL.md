---
name: agent-card-hooks
description: Guide for implementing fast-agent hooks and user-invoked command actions. Use when adding hook functions to agent cards or Python code for tasks like history compaction, saving sessions, modifying tool calls, managing agent lifecycle, or adding explicit slash-command add-ins with PluginCommandActionContext.
---

# Implement agent hooks and command actions

Hooks let you intercept and customize agent behavior at specific points in the
tool loop (per-turn) or agent lifecycle (start/shutdown).

Command actions are related but explicit: users invoke them with `/command` or
optional TUI keybindings. Use command actions for add-ins such as editing recent
history, drafting the next user message, or asking another agent to review
context.

**Audience**: Developers adding custom hook logic to fast-agent agents.

## Quick workflow

1. Decide whether the behavior should be automatic (hook) or user-invoked (command action).
2. Implement async functions with the correct context type.
3. Wire hooks via agent card YAML/Python class assignment, or wire command actions via `commands:`.
4. Test with the smoke test script, slash commands, or real agents. You may need the User to assist with this step.

## Choosing hooks vs command actions

| Use | Choose | Why |
| --- | --- | --- |
| Always trim history after each turn | Hook | Automatic lifecycle behavior |
| Save history after each completed turn | Hook | No user decision required |
| Start/stop an external service with an agent | Lifecycle hook | Agent instance lifecycle |
| Draft the next user message into the input buffer | Command action | User should review before submitting |
| Edit or annotate the previous assistant message | Command action | Explicit user-directed history change |
| Ask `critic` to review recent context on demand | Command action | User chooses when to run it |

## Hook points

### Tool loop hooks

Run during the LLM/tool execution cycle. Configure via `tool_hooks:` in agent cards
or `ToolRunnerHooks` in Python.

| Hook                  | When it fires                                         |
| --------------------- | ----------------------------------------------------- |
| `before_llm_call`     | Before each LLM call (receives pending messages)      |
| `after_llm_call`      | After each assistant response                         |
| `before_tool_call`    | Before executing tool calls                           |
| `after_tool_call`     | After tool results are received                       |
| `after_turn_complete` | Once after the turn finishes (stop reason ≠ TOOL_USE) |

### Lifecycle hooks

Run when agent instances start or shut down. Configure via `lifecycle_hooks:` in
agent cards or `AgentLifecycleHooks` in Python.

| Hook          | When it fires               |
| ------------- | --------------------------- |
| `on_start`    | During agent initialization |
| `on_shutdown` | During agent shutdown       |

### Built-in shortcut

Set `trim_tool_history: true` in agent cards to apply the history trimmer after each turn.

## Approach 1: Agent card YAML

Reference hook functions using `module.py:function` specs. Paths are resolved
relative to the agent card location.

```yaml
tool_hooks:
  before_llm_call: hooks.py:log_pending_messages
  after_turn_complete: hooks.py:save_after_turn

lifecycle_hooks:
  on_start: hooks.py:start_service
  on_shutdown: hooks.py:stop_service
```

Hook functions must be `async def` with the appropriate context type:

```python
# hooks.py
from fast_agent.hooks import HookContext, AgentLifecycleContext

async def save_after_turn(ctx: HookContext) -> None:
    if ctx.is_turn_complete:
        # Access and modify history
        history = ctx.message_history
        ctx.load_message_history(history[-10:])

async def start_service(ctx: AgentLifecycleContext) -> None:
    # Store state on the agent instance
    ctx.agent._service_handle = "started"
```

## Approach 2: Python classes

For programmatic control, assign hooks directly to agent instances or use the
dataclass constructors.

```python
from fast_agent.agents.tool_runner import ToolRunnerHooks
from fast_agent.hooks.lifecycle_hook_loader import AgentLifecycleHooks

# Tool loop hooks
async def my_after_turn(runner, message):
    print(f"Turn complete: {message.stop_reason}")

hooks = ToolRunnerHooks(after_turn_complete=my_after_turn)
agent.tool_runner_hooks = hooks

# Lifecycle hooks
async def my_on_start(ctx):
    print(f"Agent {ctx.agent_name} starting")

lifecycle = AgentLifecycleHooks(on_start=my_on_start)
```

Note: Python class hooks use raw signatures `(runner, message)` while agent card
hooks receive a `HookContext` wrapper.

## Hook context objects

### HookContext (tool hooks via agent cards)

```python
from fast_agent.hooks import HookContext

async def my_hook(ctx: HookContext) -> None:
    ctx.agent_name      # Agent name
    ctx.iteration       # Current tool loop iteration
    ctx.is_turn_complete # True if stop_reason != TOOL_USE
    ctx.message_history # Current message history
    ctx.message         # The message that triggered this hook
    ctx.hook_type       # "before_llm_call", "after_turn_complete", etc.
    ctx.usage           # Token usage stats (UsageAccumulator | None)
    ctx.context         # Agent's Context object if available
    ctx.get_agent(name) # Look up another agent by name
    ctx.load_message_history(messages)  # Replace history
```

### AgentLifecycleContext (lifecycle hooks)

```python
from fast_agent.hooks import AgentLifecycleContext

async def my_hook(ctx: AgentLifecycleContext) -> None:
    ctx.agent_name      # Agent name
    ctx.agent           # The agent instance
    ctx.context         # Context object (or None)
    ctx.config          # AgentConfig
    ctx.hook_type       # "on_start" or "on_shutdown"
    ctx.has_context     # True if context is available
    ctx.get_agent(name) # Look up another agent by name
```

## Hook output helpers

Use these to render consistent status messages to users:

```python
from fast_agent.hooks import show_hook_message, show_hook_failure

async def my_hook(ctx: HookContext) -> None:
    # Show status message (yellow prefix)
    show_hook_message(
        ctx,
        "trimmed 6 messages",
        hook_name="after_turn_complete",
        hook_kind="tool",
    )

    # Show failure (red prefix) - typically before re-raising
    try:
        ...
    except Exception as exc:
        show_hook_failure(ctx, hook_name="my_hook", hook_kind="tool", error=exc)
        raise
```

## Built-in hooks

| Hook                     | Import             | Purpose                         |
| ------------------------ | ------------------ | ------------------------------- |
| `trim_tool_loop_history` | `fast_agent.hooks` | Compact tool call/result pairs  |
| `save_session_history`   | `fast_agent.hooks` | Save history to session storage |

## Using built-in hooks

The built-ins can be wired directly in agent cards (typically as
`after_turn_complete` hooks) or via the `trim_tool_history: true` shortcut.

**Trim tool loops (explicit hook):**

```yaml
tool_hooks:
  after_turn_complete: fast_agent.hooks.history_trimmer:trim_tool_loop_history
```

**Trim tool loops (shortcut):**

```yaml
trim_tool_history: true
```

**Save session history:**

```yaml
tool_hooks:
  after_turn_complete: fast_agent.hooks:save_session_history
```

## Sharing state between hooks

**Agent attribute storage** (recommended):

```python
async def on_start(ctx: AgentLifecycleContext) -> None:
    ctx.agent._my_state = {"started": True}

async def after_turn(ctx: HookContext) -> None:
    state = getattr(ctx.agent, "_my_state", {})
```

**Cross-agent access**:

```python
async def my_hook(ctx: HookContext) -> None:
    companion = ctx.get_agent("helper-agent")
    if companion:
        # Access companion agent
        ...
```

**Example: translate the assistant response via a helper agent** (the helper must be
configured in the same app, e.g. `agents: [translator]` in the card):

```python
from mcp.types import TextContent
from fast_agent.hooks import show_hook_message

async def translate_after_turn(ctx: HookContext) -> None:
    if not ctx.is_turn_complete:
        return

    translator = ctx.get_agent("translator")
    if translator is None:
        return

    history = ctx.message_history
    for message in reversed(history):
        if message.role != "assistant":
            continue
        text = message.all_text().strip()
        if not text:
            return

        translated = await translator.send(
            "Translate the following assistant response into French. "
            "Reply with the translation only.\n\n"
            f"{text}"
        )
        message.content = [TextContent(type="text", text=translated)]
        ctx.load_message_history(list(history))
        show_hook_message(
            ctx,
            "translated assistant response to French",
            hook_name="translate",
            hook_kind="extension",
        )
        return
```

Related example files:

- `assets/examples/translate_hook.py`
- `assets/examples/hook_translate_agent.md`
- `assets/examples/translator_agent.md`

## Command actions

Command actions are async Python add-ins invoked by users:

```text
/draft-next concise
/review-last critic
```

They can be configured globally in `fast-agent.yaml` or on an AgentCard.
Built-in slash commands win first, AgentCard commands win over global commands,
and unknown commands fall through normally.

Global config:

```yaml
commands:
  draft-next:
    description: Draft the next user message
    input_hint: "[format]"
    handler: "./command-actions.py:draft_next"
    key: "c-x d"
```

AgentCard frontmatter:

```yaml
---
type: smart
name: dev
commands:
  review-last:
    description: Ask another agent to review the latest response
    input_hint: "[agent-name]"
    handler: "./commands.py:review_last"
---
```

Handler functions receive `PluginCommandActionContext` and return
`PluginCommandActionResult`, `str`, or `None`:

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

Key command-action points:

- `buffer_prefill` replaces the TUI input buffer but does not submit.
- `ctx.get_agent(name)` can call another configured agent.
- `ctx.message_history` and `ctx.load_message_history(...)` can inspect/mutate current history.
- `ctx.mark_user_adjusted(message, note=...)` records provenance in `fast-agent.audit`.
- For editor-backed commands, run the blocking editor in `asyncio.to_thread(...)`,
  use `ctx.session_cwd` as the subprocess cwd when available, and return
  reviewable edits as `buffer_prefill` unless you intentionally mutate history.
- Do not swallow editor failures with broad `except Exception`; return a concise
  `PluginCommandActionResult(message=...)` for expected `subprocess`/I/O errors.
- Relative handler paths in AgentCards resolve from the AgentCard directory.
- Relative handler paths in global config resolve from the resolved `fast-agent.yaml`.

See [references/command-actions.md](references/command-actions.md) for the detailed API,
including a complete `$VISUAL`/`$EDITOR` `/editlast` example.

## Testing hooks

### Smoke test script

Use the bundled smoke test to run a hook against saved history without a full agent:

```bash
python scripts/hook_smoke_test.py \
  --hook path/to/hooks.py:after_turn_complete \
  --history ./history.json \
  --hook-type after_turn_complete \
  --output ./history-modified.json
```

Options:

- `--hook` (required): Hook spec in `module.py:function` format
- `--history` (required): Path to history file (JSON or delimited)
- `--hook-type`: Hook type label for HookContext (default: `after_turn_complete`)
- `--output`: Save modified history to this path
- `--agent-name`: Agent name for the test context
- `--base-path`: Resolve relative hook paths from this directory

### Integration testing

For full integration tests:

- Use real agents with `PassthroughLLM` subclasses to drive tool calls
- Use `tmp_path` for files written during tests
- See `tests/integration/tool_hooks/` and `tests/integration/agent_hooks/`

Run checks after changes:

```bash
uv run scripts/lint.py --fix
uv run scripts/typecheck.py
pytest tests/unit
```

## Bundled examples

Example hook implementations are provided in `assets/examples/`:

| File                    | Hook type             | What it demonstrates                                  |
| ----------------------- | --------------------- | ----------------------------------------------------- |
| `cache_rate_display.py` | `after_turn_complete` | Rich text output with `show_hook_message`             |
| `append_context.py`     | `before_llm_call`     | Appending messages via `ctx.runner.append_messages()` |
| `save_history.py`       | `after_turn_complete` | Saving history to timestamped files                   |
| `fix_tool_calls.py`     | `before_tool_call`    | Modifying tool calls before execution                 |

Copy and adapt these for your use case.

## References

- [references/hook-api.md](references/hook-api.md) — Detailed API reference with all types and signatures
- [references/command-actions.md](references/command-actions.md) — Command action configuration and handler API
