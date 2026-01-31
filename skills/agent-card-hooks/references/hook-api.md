# Hook API reference

## Agent card fields

```yaml
# Tool loop hooks (per turn/tool loop)
tool_hooks:
  before_llm_call: hooks.py:fn
  after_llm_call: hooks.py:fn
  before_tool_call: hooks.py:fn
  after_tool_call: hooks.py:fn
  after_turn_complete: hooks.py:fn

# Lifecycle hooks (per agent instance)
lifecycle_hooks:
  on_start: hooks.py:fn
  on_shutdown: hooks.py:fn

# Shortcut for built-in trimmer
trim_tool_history: true
```

Hook specs use `module.py:function` format, resolved relative to the agent card path.
Invalid hook types raise `AgentConfigError` during card parsing.

## Python hook classes

### ToolRunnerHooks

For programmatic tool loop hooks. Assign to `agent.tool_runner_hooks`.

```python
from fast_agent.agents.tool_runner import ToolRunnerHooks

@dataclass(frozen=True)
class ToolRunnerHooks:
    before_llm_call: Callable[[ToolRunner, list[PromptMessageExtended]], Awaitable[None]] | None
    after_llm_call: Callable[[ToolRunner, PromptMessageExtended], Awaitable[None]] | None
    before_tool_call: Callable[[ToolRunner, PromptMessageExtended], Awaitable[None]] | None
    after_tool_call: Callable[[ToolRunner, PromptMessageExtended], Awaitable[None]] | None
    after_turn_complete: Callable[[ToolRunner, PromptMessageExtended], Awaitable[None]] | None
```

### AgentLifecycleHooks

For programmatic lifecycle hooks.

```python
from fast_agent.hooks.lifecycle_hook_loader import AgentLifecycleHooks

@dataclass(frozen=True)
class AgentLifecycleHooks:
    on_start: Callable[[AgentLifecycleContext], Awaitable[None]] | None
    on_shutdown: Callable[[AgentLifecycleContext], Awaitable[None]] | None
```

## Context objects

### HookContext

Passed to agent card tool hooks. Source: `src/fast_agent/hooks/hook_context.py`

```python
from fast_agent.hooks import HookContext

@dataclass
class HookContext:
    runner: HookRunner           # The tool runner instance
    agent: MessageHistoryAgentProtocol  # The agent instance
    message: PromptMessageExtended      # Current message
    hook_type: str               # "before_llm_call", "after_turn_complete", etc.

    # Properties
    agent_name: str              # Agent name
    iteration: int               # Current tool loop iteration
    is_turn_complete: bool       # True if stop_reason != TOOL_USE
    message_history: list[PromptMessageExtended]  # Current history
    usage: UsageAccumulator | None    # Token usage stats
    context: Context | None      # Agent's Context object
    agent_registry: Mapping[str, AgentProtocol] | None  # All agents

    # Methods
    def get_agent(name: str) -> AgentProtocol | None  # Lookup agent by name
    def load_message_history(messages: list[PromptMessageExtended]) -> None  # Replace history
```

### AgentLifecycleContext

Passed to lifecycle hooks. Source: `src/fast_agent/hooks/lifecycle_hook_context.py`

```python
from fast_agent.hooks import AgentLifecycleContext

@dataclass
class AgentLifecycleContext:
    agent: AgentProtocol         # The agent instance
    context: Context | None      # Context object (may be None)
    config: AgentConfig          # Agent configuration
    hook_type: Literal["on_start", "on_shutdown"]

    # Properties
    agent_name: str              # Agent name
    has_context: bool            # True if context is available
    agent_registry: Mapping[str, AgentProtocol] | None  # All agents

    # Methods
    def get_agent(name: str) -> AgentProtocol | None  # Lookup agent by name
```

## ToolRunner helpers

Available inside Python class hooks via the `runner` parameter:

```python
runner.iteration           # Current loop count
runner.delta_messages      # Pending messages for next LLM call
runner.set_request_params(params)  # Update request parameters
runner.append_messages(msg)        # Add messages to pending
```

## Output helpers

### show_hook_message

Render a status line with consistent formatting:

```python
from fast_agent.hooks import show_hook_message

show_hook_message(
    ctx,                    # HookContext or object with .agent attribute
    "trimmed 6 messages",   # Message text (str or rich.Text)
    hook_name="my_hook",    # Hook name (shown dimmed)
    hook_kind="tool",       # "tool" or "agent"
    style="bright_yellow",  # Prefix color (default: bright_yellow)
)
```

### show_hook_failure

Render a red failure banner:

```python
from fast_agent.hooks import show_hook_failure

show_hook_failure(
    ctx,
    hook_name="my_hook",
    hook_kind="tool",
    error=exc,              # Optional exception
)
```

## PromptMessageExtended essentials

Common fields used in hooks:

```python
message.role              # "user" | "assistant"
message.content           # list[ContentBlock]
message.tool_calls        # dict[str, ToolCall] | None
message.tool_results      # list[ToolResult] | None
message.stop_reason       # LlmStopReason enum

# Helpers
message.first_text()      # First text content
message.last_text()       # Last text content
message.all_text()        # All text content joined
```

## Built-in hooks

| Function | Module | Purpose |
|----------|--------|---------|
| `trim_tool_loop_history` | `fast_agent.hooks` | Compact tool call/result pairs in history |
| `save_session_history` | `fast_agent.hooks` | Save history to session storage |

## Source files

| Component | Location |
|-----------|----------|
| HookContext | `src/fast_agent/hooks/hook_context.py` |
| AgentLifecycleContext | `src/fast_agent/hooks/lifecycle_hook_context.py` |
| ToolRunnerHooks | `src/fast_agent/agents/tool_runner.py` |
| AgentLifecycleHooks | `src/fast_agent/hooks/lifecycle_hook_loader.py` |
| Hook loader | `src/fast_agent/tools/hook_loader.py` |
| Lifecycle hook loader | `src/fast_agent/hooks/lifecycle_hook_loader.py` |
| Output helpers | `src/fast_agent/hooks/hook_messages.py` |
| History trimmer | `src/fast_agent/hooks/history_trimmer.py` |

## Test references

| Test type | Location |
|-----------|----------|
| Tool hooks integration | `tests/integration/tool_hooks/test_tool_hooks.py` |
| Lifecycle hooks integration | `tests/integration/agent_hooks/test_agent_lifecycle_hooks.py` |
| History trimmer unit | `tests/unit/fast_agent/hooks/test_history_trimmer.py` |
| Tool runner hooks unit | `tests/unit/fast_agent/agents/test_tool_runner_hooks.py` |
