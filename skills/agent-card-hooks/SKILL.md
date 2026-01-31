---
name: agent-card-hooks
description: Guide for implementing fast-agent hooks. Use when adding hook functions to agent cards or Python code for tasks like history compaction, saving sessions, modifying tool calls, or managing agent lifecycle.
---

# Implement agent hooks

Hooks let you intercept and customize agent behavior at specific points in the
tool loop (per-turn) or agent lifecycle (start/shutdown).

**Audience**: Developers adding custom hook logic to fast-agent agents.

## Quick workflow

1. Identify which hook points you need (tool loop vs lifecycle).
2. Implement async hook functions with the correct context type.
3. Wire hooks via agent card YAML or Python class assignment.
4. Test hooks with the smoke test script or real agents. You may need the User to assist with this step.

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
