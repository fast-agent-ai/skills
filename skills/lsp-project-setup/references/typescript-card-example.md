# TypeScript LSP Agent Card Example

Place this card in `.fast-agent/agent-cards/dev.md` (or similar name).

## Complete Example

```markdown
---
name: dev
default: true
function_tools:
  - multilspy_tools_ts.py:lsp_hover
  - multilspy_tools_ts.py:lsp_definition
  - multilspy_tools_ts.py:lsp_references
  - multilspy_tools_ts.py:lsp_document_symbols
  - multilspy_tools_ts.py:lsp_workspace_symbols
  - multilspy_tools_ts.py:lsp_diagnostics
---

You are a development assistant for this TypeScript project.

{{file_silent:tsconfig.json}}

## Finding and Searching

Use LSP function tools for code navigation (definitions, references, symbols, hover, diagnostics).
Prefer LSP tools over text search for structural queries.

{{serverInstructions}}
{{agentSkills}}
{{env}}

The current date is {{currentDate}}.
```

## Notes

- The `multilspy_tools_ts.py` file must exist alongside the card (or use absolute path).
- `default: true` makes this the default agent for `fast-agent go`.
- `{{file_silent:tsconfig.json}}` includes TypeScript config; empty if missing.
- Add `agents: [ripgrep_search]` if you have a ripgrep sub-agent for text search.
- Add `shell: true` to enable shell command execution.
