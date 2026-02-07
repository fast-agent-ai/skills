from __future__ import annotations

from typing import TYPE_CHECKING

from mcp.types import CallToolResult, TextContent

from fast_agent.hooks import HookContext, show_hook_message
from fast_agent.hooks.history_trimmer import trim_tool_loop_history
from fast_agent.mcp.helpers.content_helpers import get_text
from fast_agent.types import PromptMessageExtended, split_into_turns

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

DEFAULT_OMITTED_TEXT = "(tool result omitted)"
DEFAULT_COMPACTION_PROMPT = (
    "Summarize the conversation so far. Preserve user goals, constraints, "
    "decisions, and open tasks. Be concise."
)


def _flatten_turns(turns: list[list[PromptMessageExtended]]) -> list[PromptMessageExtended]:
    return [msg for turn in turns for msg in turn]


def _keep_last_turns(
    messages: list[PromptMessageExtended],
    turns: int,
) -> list[PromptMessageExtended]:
    if turns <= 0:
        return []
    all_turns = split_into_turns(messages)
    if len(all_turns) <= turns:
        return messages
    return _flatten_turns(all_turns[-turns:])


def _estimate_tokens(messages: list[PromptMessageExtended]) -> int:
    # Simple heuristic: ~4 chars per token
    return sum(max(1, len(msg.all_text()) // 4) for msg in messages)


def _strip_tool_results(
    results: dict[str, CallToolResult],
    *,
    placeholder: str,
) -> dict[str, CallToolResult]:
    stripped: dict[str, CallToolResult] = {}
    for tool_id, result in results.items():
        stripped[tool_id] = CallToolResult(
            content=[TextContent(type="text", text=placeholder)],
            structuredContent=None,
            isError=result.isError,
        )
    return stripped


def _tool_result_text(result: CallToolResult) -> str:
    parts: list[str] = []
    for content in result.content:
        text = get_text(content)
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def _format_history(messages: list[PromptMessageExtended]) -> str:
    blocks: list[str] = []
    for msg in messages:
        text = msg.all_text().strip()
        if text:
            blocks.append(f"{msg.role}:\n{text}")
        if msg.tool_calls:
            tool_names = ", ".join(call.params.name for call in msg.tool_calls.values())
            blocks.append(f"{msg.role} TOOL_CALLS: {tool_names}")
        if msg.tool_results:
            for tool_id, result in msg.tool_results.items():
                result_text = _tool_result_text(result)
                if result_text:
                    blocks.append(f"TOOL_RESULT {tool_id}:\n{result_text}")
    return "\n\n".join(blocks).strip()


def _get_sender(
    target_agent: object,
) -> Callable[[str], Awaitable[str]] | None:
    send = getattr(target_agent, "send", None)
    if callable(send):
        return send
    return None


async def rolling_window(ctx: HookContext, *, turns: int = 8) -> None:
    if not ctx.is_turn_complete:
        return
    history = ctx.message_history
    trimmed = _keep_last_turns(history, turns)
    if len(trimmed) == len(history):
        return
    ctx.load_message_history(trimmed)
    show_hook_message(
        ctx, f"kept last {turns} turns", hook_name="rolling_window", hook_kind="tool"
    )


async def truncate_over_threshold(
    ctx: HookContext,
    *,
    threshold_percent: float = 85.0,
    max_tokens: int | None = 12000,
    keep_turns: int = 6,
) -> None:
    if not ctx.is_turn_complete:
        return

    usage = ctx.usage
    if usage and usage.context_usage_percentage is not None:
        if usage.context_usage_percentage <= threshold_percent:
            return
    else:
        if max_tokens is None:
            return
        if _estimate_tokens(ctx.message_history) <= max_tokens:
            return

    history = ctx.message_history
    trimmed = _keep_last_turns(history, keep_turns)
    if len(trimmed) == len(history):
        return

    ctx.load_message_history(trimmed)
    show_hook_message(
        ctx,
        f"trimmed history (threshold {threshold_percent}%, kept {keep_turns} turns)",
        hook_name="truncate_over_threshold",
        hook_kind="tool",
    )


async def clear_results_soft(
    ctx: HookContext,
    *,
    placeholder: str = DEFAULT_OMITTED_TEXT,
) -> None:
    if not ctx.is_turn_complete:
        return

    history = ctx.message_history
    updated: list[PromptMessageExtended] = []
    changed = False

    for message in history:
        if not message.tool_results:
            updated.append(message)
            continue

        msg_copy = message.model_copy(deep=True)
        msg_copy.tool_results = _strip_tool_results(
            message.tool_results,
            placeholder=placeholder,
        )
        updated.append(msg_copy)
        changed = True

    if not changed:
        return

    ctx.load_message_history(updated)
    show_hook_message(
        ctx,
        "cleared tool result payloads",
        hook_name="clear_results_soft",
        hook_kind="tool",
    )


async def clear_results_hard(ctx: HookContext) -> None:
    if not ctx.is_turn_complete:
        return

    before = len(ctx.message_history)
    await trim_tool_loop_history(ctx)
    after = len(ctx.message_history)
    if after < before:
        show_hook_message(
            ctx,
            "trimmed tool loop history",
            hook_name="clear_results_hard",
            hook_kind="tool",
        )


async def compaction_prompt(
    ctx: HookContext,
    *,
    keep_turns: int = 2,
    min_turns: int = 6,
    compactor_agent: str | None = None,
    prompt: str = DEFAULT_COMPACTION_PROMPT,
) -> None:
    if not ctx.is_turn_complete:
        return

    history = ctx.message_history
    turns = split_into_turns(history)
    if len(turns) <= max(min_turns, keep_turns + 1):
        return

    recent = _flatten_turns(turns[-keep_turns:])
    to_summarize = _flatten_turns(turns[:-keep_turns])
    if not to_summarize:
        return

    transcript = _format_history(to_summarize)
    if not transcript:
        return

    target_agent = ctx.get_agent(compactor_agent) if compactor_agent else ctx.agent
    sender = _get_sender(target_agent)
    if sender is None:
        return

    summary_text = await sender(f"{prompt}\n\n{transcript}")
    summary_message = PromptMessageExtended(
        role="assistant",
        content=[TextContent(type="text", text=summary_text)],
    )

    ctx.load_message_history([summary_message, *recent])
    show_hook_message(
        ctx,
        "compacted history with summary prompt",
        hook_name="compaction_prompt",
        hook_kind="tool",
    )
