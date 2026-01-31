"""Example: Display cache hit/write rates after each turn using Rich text."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from rich.text import Text

from fast_agent.constants import FAST_AGENT_USAGE
from fast_agent.hooks import show_hook_message
from fast_agent.mcp.helpers.content_helpers import get_text

if TYPE_CHECKING:
    from fast_agent.hooks import HookContext


def _usage_payload_from_channels(ctx: "HookContext") -> dict[str, object] | None:
    """Extract usage payload from message channels."""
    channels = ctx.message.channels or {}
    usage_blocks = channels.get(FAST_AGENT_USAGE, [])
    if not usage_blocks:
        return None

    payload_text = get_text(usage_blocks[0])
    if not payload_text:
        return None

    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        return None

    return payload if isinstance(payload, dict) else None


def _coerce_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return None


def _cache_rates(ctx: "HookContext") -> tuple[float | None, float | None]:
    """Calculate cache read and write percentages from usage data."""
    payload = _usage_payload_from_channels(ctx)
    if not payload:
        return None, None

    turn_payload = payload.get("turn")
    if not isinstance(turn_payload, dict):
        return None, None

    cache_payload = turn_payload.get("cache_usage")
    if not isinstance(cache_payload, dict):
        return None, None

    input_tokens_raw = turn_payload.get("display_input_tokens") or turn_payload.get("input_tokens")
    input_tokens = _coerce_int(input_tokens_raw)
    if input_tokens is None or input_tokens <= 0:
        return None, None

    cache_read_tokens = _coerce_int(cache_payload.get("cache_read_tokens")) or 0
    cache_hit_tokens = _coerce_int(cache_payload.get("cache_hit_tokens")) or 0
    cache_write_tokens = _coerce_int(cache_payload.get("cache_write_tokens")) or 0

    cache_read_total = cache_read_tokens + cache_hit_tokens
    cache_read_pct = cache_read_total / input_tokens
    cache_write_pct = (cache_write_tokens / input_tokens) if cache_write_tokens > 0 else None

    return cache_read_pct, cache_write_pct


def _progress_bar(percent: float, width: int = 20, fill_style: str = "bright_cyan") -> Text:
    """Render a text-based progress bar."""
    percent = max(0.0, min(percent, 1.0))
    filled = int(round(percent * width))
    bar = Text("|", style="dim")
    if filled:
        bar.append("█" * filled, style=fill_style)
    if filled < width:
        bar.append("░" * (width - filled), style="dim")
    bar.append("|", style="dim")
    bar.append(f" {percent * 100:5.1f}%", style="dim")
    return bar


async def after_turn_complete(ctx: "HookContext") -> None:
    """Display cache read/write rates after each turn completes."""
    cache_read_pct, cache_write_pct = _cache_rates(ctx)
    
    if cache_read_pct is not None:
        line = Text("", style="dim")
        line.append_text(_progress_bar(cache_read_pct))
        show_hook_message(ctx, line, hook_name="cache_read_rate", hook_kind="tool")
    
    if cache_write_pct is not None:
        line = Text("cache write rate ", style="dim")
        line.append_text(_progress_bar(cache_write_pct, fill_style="bright_yellow"))
        show_hook_message(ctx, line, hook_name="cache_write_rate", hook_kind="tool")
