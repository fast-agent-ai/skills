"""Example: Save message history to a timestamped file after each turn."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import TYPE_CHECKING

from fast_agent.mcp.prompt_serialization import save_messages

if TYPE_CHECKING:
    from fast_agent.hooks import HookContext


async def save_history_to_file(ctx: "HookContext") -> None:
    """
    Save the turn's messages to a timestamped JSON file.

    File format: <agent_name>-yyyy-mm-dd-hh-mm-ss.json
    
    Handles both use_history: true (messages in ctx.message_history)
    and use_history: false (messages in ctx.runner.delta_messages).
    """
    agent_name = ctx.agent.name
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{agent_name}-{timestamp}.json"

    messages = ctx.message_history
    if not messages:
        # Fall back to runner's turn messages + final response
        runner_messages = getattr(ctx.runner, "delta_messages", None)
        if isinstance(runner_messages, Iterable):
            messages = list(runner_messages)
        else:
            messages = []
        if ctx.message and ctx.message not in messages:
            messages.append(ctx.message)

    save_messages(messages, filename)
