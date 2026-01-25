# Shared LSP Development Instructions

Include this text in agent card instructions for LSP-enabled development agents.

## Standard Instruction Block

```markdown
## Finding and Searching

Use LSP function tools for code navigation (definitions, references, symbols, hover, diagnostics).
Prefer LSP tools over text search for structural queries. Use ripgrep for broad text discovery or file operations.

## Quality

Run linting and type checking after code changes to catch issues early.
```

## Template Variables

Include these in agent card instructions as needed:

- `{{serverInstructions}}` - MCP server tool descriptions
- `{{agentSkills}}` - Available skills metadata
- `{{env}}` - Environment info (platform, workspace root, client)
- `{{currentDate}}` - Current date for time-sensitive tasks
