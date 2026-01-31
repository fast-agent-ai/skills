"""Example: Fix common tool call issues before execution."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fast_agent.core.logging.logger import get_logger

if TYPE_CHECKING:
    from fast_agent.hooks import HookContext

logger = get_logger(__name__)

# Map of incorrect tool names to correct ones
TOOL_NAME_CORRECTIONS = {
    "exec": "execute",
    "executescript": "execute",
    "execscript": "execute",
    "executor": "execute",
    "exec_command": "execute",
}


async def fix_tool_calls(ctx: "HookContext") -> None:
    """
    Fix common tool call issues before execution.
    
    1. Corrects hallucinated tool name variations (exec* → execute)
    2. Strips invalid -R flag from ripgrep commands
    
    Wire this to before_tool_call in your agent card:
        tool_hooks:
          before_tool_call: fix_tool_calls.py:fix_tool_calls
    """
    if ctx.hook_type != "before_tool_call":
        return
    
    if not ctx.message.tool_calls:
        return
    
    for tool_id, tool_call in ctx.message.tool_calls.items():
        original_name = tool_call.params.name
        
        # Fix 1: Correct hallucinated tool names
        if original_name in TOOL_NAME_CORRECTIONS:
            corrected = TOOL_NAME_CORRECTIONS[original_name]
            tool_call.params.name = corrected
            logger.warning(
                "Corrected tool name",
                data={"original": original_name, "corrected": corrected},
            )
        elif original_name.startswith("exec") and original_name != "execute":
            tool_call.params.name = "execute"
            logger.warning(
                "Corrected exec* variant",
                data={"original": original_name, "corrected": "execute"},
            )
        
        # Fix 2: Strip -R flag from ripgrep commands
        if tool_call.params.name != "execute":
            continue
        
        args = tool_call.params.arguments
        if not isinstance(args, dict):
            continue
        
        command = args.get("command")
        if not command or not isinstance(command, str) or "rg" not in command:
            continue
        
        original_command = command
        command = command.replace(" -R ", " ").replace(" -R\n", "\n")
        if command.endswith(" -R"):
            command = command[:-3]
        
        if command != original_command:
            args["command"] = command
            logger.warning(
                "Stripped invalid -R flag from ripgrep",
                data={"original": original_command, "modified": command},
            )
