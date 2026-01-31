"""Example: Translate assistant responses using a helper agent."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp.types import TextContent

from fast_agent.hooks import show_hook_message

if TYPE_CHECKING:
    from fast_agent.hooks import HookContext
    from fast_agent.mcp.prompt_message_extended import PromptMessageExtended


def _last_assistant_text(
    history: list["PromptMessageExtended"],
) -> tuple["PromptMessageExtended", str] | None:
    for message in reversed(history):
        if message.role != "assistant":
            continue
        text = message.all_text().strip()
        if text:
            return message, text
    return None


async def translate_after_turn(ctx: "HookContext") -> None:
    """Translate the most recent assistant message after each turn."""
    if not ctx.is_turn_complete:
        return

    translator = ctx.get_agent("translator")
    if translator is None:
        show_hook_message(
            ctx,
            "translator agent not available",
            hook_name="translate",
            hook_kind="extension",
        )
        return

    target = _last_assistant_text(ctx.message_history)
    if target is None:
        return

    message, text = target
    translated = await translator.send(
        "Translate the following assistant response into French. "
        "Reply with the translation only.\n\n"
        f"{text}"
    )

    message.content = [TextContent(type="text", text=translated)]
    ctx.load_message_history(list(ctx.message_history))
    show_hook_message(
        ctx,
        "translated assistant response to French",
        hook_name="translate",
        hook_kind="extension",
    )
