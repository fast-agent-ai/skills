# Hook API reference (agent cards)

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

Notes:
- Hook specs use `module.py:function` and are resolved relative to the card path
  (`src/fast_agent/tools/hook_loader.py`, `src/fast_agent/agents/llm_decorator.py`).
- Invalid hook types raise `AgentConfigError` during card parsing.

## Tool hook types
Defined in `fast_agent.tools.hook_loader.VALID_HOOK_TYPES` and executed in
`fast_agent.agents.tool_runner.ToolRunner`:

- `before_llm_call`: before each LLM call (receives pending delta messages).
- `after_llm_call`: after each assistant response.
- `before_tool_call`: before executing tool calls.
- `after_tool_call`: after tool results are received.
- `after_turn_complete`: once after the turn finishes (stop reason != TOOL_USE).

## Lifecycle hook types
Defined in `fast_agent.hooks.lifecycle_hook_loader.VALID_LIFECYCLE_HOOK_TYPES`:

- `on_start`: called during `LlmDecorator.initialize()`.
- `on_shutdown`: called during `LlmDecorator.shutdown()`.

## Hook contexts
### HookContext (tool hooks)
File: `src/fast_agent/hooks/hook_context.py`

```py
@dataclass
class HookContext:
    runner: HookRunner
    agent: MessageHistoryAgentProtocol
    message: PromptMessageExtended
    hook_type: str

    @property
    def agent_name(self) -> str: ...
    @property
    def iteration(self) -> int: ...
    @property
    def is_turn_complete(self) -> bool: ...
    @property
    def message_history(self) -> list[PromptMessageExtended]: ...
    def load_message_history(self, messages: list[PromptMessageExtended]) -> None: ...
```

Key behaviors:
- `hook_loader._create_hook_wrapper()` supplies `ctx.message` from the hook’s
  signature. `before_llm_call` uses the last message from the list.
- `ctx.agent` is always `runner._agent` (so cloned agents get the right instance).

### AgentLifecycleContext (lifecycle hooks)
File: `src/fast_agent/hooks/lifecycle_hook_context.py`

```py
@dataclass
class AgentLifecycleContext:
    agent: AgentProtocol
    context: Context | None
    config: AgentConfig
    hook_type: Literal["on_start", "on_shutdown"]

    @property
    def agent_name(self) -> str: ...
    @property
    def has_context(self) -> bool: ...
```

## ToolRunner helpers you can use inside hooks
File: `src/fast_agent/agents/tool_runner.py`

- `runner.set_request_params(params)`
- `runner.append_messages("text" | PromptMessageExtended)`
- `runner.delta_messages` (pending messages for next LLM call)
- `runner.iteration` (current loop count)

## PromptMessageExtended essentials
File: `src/fast_agent/mcp/prompt_message_extended.py`

Fields commonly used in hooks:
- `role` (`"user" | "assistant"`)
- `content` (list of MCP ContentBlock)
- `tool_calls` / `tool_results`
- `stop_reason` (`LlmStopReason.TOOL_USE`, `LlmStopReason.END_TURN`, etc.)
- helpers: `.first_text()`, `.last_text()`, `.all_text()`

## Built-in hooks + examples
- History trimmer: `fast_agent.hooks.history_trimmer:trim_tool_loop_history`
- Session saver: `fast_agent.hooks.session_history:save_session_history`
- Example hook modules:
  - `examples/hf-toad-cards/hooks/save_history.py`
  - `examples/hf-toad-cards/hooks/fix_ripgrep_tool_calls.py`

## Testing references
- Tool hooks: `tests/integration/tool_hooks/test_tool_hooks.py`
- Lifecycle hooks: `tests/integration/agent_hooks/test_agent_lifecycle_hooks.py`
- Tool runner unit hooks: `tests/unit/fast_agent/agents/test_tool_runner_hooks.py`
