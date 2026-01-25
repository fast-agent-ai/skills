---
name: agent-card-hooks
description: Guide for implementing fast-agent agent card tool hooks and lifecycle hooks. Use when you need to add hook functions to agent cards (tool_hooks, lifecycle_hooks, trim_tool_history) for tasks like compaction, saving history, modifying tool calls, or starting/shutting down external services. Covers available hook types, shared context patterns, required types, and testing guidance.
---

# Implement agent card hooks (tool + lifecycle)

## Quick workflow
1) Identify which hook types you need (tool loop vs agent lifecycle).
2) Implement async hook functions with the correct context type.
3) Reference hook functions from the agent card using `module.py:function` specs.
4) Share state between lifecycle + tool hooks via the agent instance or Context.
5) Add tests that exercise the hooks with real agents/LLMs (no mocking).

## Choose hook types
- Tool loop hooks: run during LLM/tool execution (`tool_hooks`).
- Lifecycle hooks: run when agent instances start/shut down (`lifecycle_hooks`).
- Built-in shortcut: `trim_tool_history: true` applies the history trimmer after each turn.

See [references/hook-api.md](references/hook-api.md) for a detailed list of hook types and context shapes.

## Implement hook modules
- Hook functions **must** be `async def`.
- Tool hook signature: `async def my_hook(ctx: HookContext) -> None`.
- Lifecycle hook signature: `async def my_hook(ctx: AgentLifecycleContext) -> None`.
- Keep hook modules next to the agent card when possible; relative paths are resolved from the card path.

Minimal examples:

```py
# hooks.py
from fast_agent.hooks.hook_context import HookContext
from fast_agent.hooks.lifecycle_hook_context import AgentLifecycleContext

async def save_after_turn(ctx: HookContext) -> None:
    if ctx.is_turn_complete:
        # read/modify history or persist
        _ = ctx.message_history

async def start_service(ctx: AgentLifecycleContext) -> None:
    ctx.agent._service_handle = "started"  # store state on the agent
```

Agent card wiring:

```yaml
lifecycle_hooks:
  on_start: hooks.py:start_service
  on_shutdown: hooks.py:stop_service

tool_hooks:
  before_tool_call: hooks.py:rewrite_tool_calls
  after_turn_complete: hooks.py:save_after_turn
```

## Share context between lifecycle + tool hooks
Use one of these patterns (pick one and document it in the hook module):

- **Agent attribute storage** (most common):
  - Set `ctx.agent.<attr>` in `on_start`.
  - Read it inside `HookContext` hooks (`ctx.agent` is the same instance).
- **Context object** (global scope):
  - Use `ctx.context` in lifecycle hooks to access shared registries/config.
  - Store global handles on `Context` (e.g., `ctx.context.<attr> = ...`).
- **External persistence**:
  - Write to files/databases for durable shared state (see hook examples below).

## Common imports
```py
from fast_agent.hooks.hook_context import HookContext
from fast_agent.hooks.lifecycle_hook_context import AgentLifecycleContext
from fast_agent.types import PromptMessageExtended, RequestParams
from fast_agent.types.llm_stop_reason import LlmStopReason
from fast_agent.context import Context
```

Useful helpers:
- `fast_agent.mcp.prompt_serialization.save_messages` for saving history.
- `fast_agent.hooks.history_trimmer.trim_tool_loop_history` for built-in trimming.
- `fast_agent.hooks.session_history.save_session_history` for session storage.

## Testing guidance (no mocks)
- Use real agents + LLMs (see integration tests under `tests/integration/tool_hooks/` and
  `tests/integration/agent_hooks/`).
- Use `PassthroughLLM` subclasses to drive tool calls or child-agent calls.
- Prefer `tmp_path` for hook files written during tests (see lifecycle hook test pattern).
- Validate both start/shutdown hook pairs and per-tool hook behavior.

When updating code, run:
- `uv run scripts/lint.py --fix`
- `uv run scripts/typecheck.py`
- `pytest tests/unit`

## Example hook patterns
- Compaction / trimming: `fast_agent.hooks.history_trimmer:trim_tool_loop_history`.
- Save history to file: `examples/hf-toad-cards/hooks/save_history.py`.
- Rewrite tool calls: `examples/hf-toad-cards/hooks/fix_ripgrep_tool_calls.py`.

For the hook API reference and type details, read:
- [references/hook-api.md](references/hook-api.md)
