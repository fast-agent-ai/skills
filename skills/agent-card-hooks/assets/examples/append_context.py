"""Example: Append context messages before each LLM call."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fast_agent.hooks import HookContext


async def before_llm_call(ctx: "HookContext") -> None:
    """
    Add guidance text before each LLM call.
    
    Only appends when there are no pending tool results (i.e., fresh user turn).
    Uses ctx.runner.append_messages() to add to the pending message list.
    """
    if ctx.message.tool_results is None:
        ctx.runner.append_messages("Use LSP for navigating python code")
