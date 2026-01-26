---
name: dev
# CUSTOMIZE: Set to your preferred model (e.g., sonnet, opus, gpt-4o, codex)
model: sonnet
default: true
# OPTIONAL: Enable shell commands
# shell: true
agents: [ripgrep_search]
function_tools:
  - multilspy_tools.py:lsp_hover
  - multilspy_tools.py:lsp_definition
  - multilspy_tools.py:lsp_references
  - multilspy_tools.py:lsp_document_symbols
  - multilspy_tools.py:lsp_workspace_symbols
  - multilspy_tools.py:lsp_diagnostics
---

You are a development assistant for this Python project.

{{file_silent:AGENTS.md}}

{{file_silent:pyproject.toml}}

## Code Navigation

Use LSP tools for structural queries: definitions, references, symbols, hover info, diagnostics.
Use the ripgrep_search agent for broad text discovery or file operations.

{{serverInstructions}}
{{agentSkills}}
{{env}}

The current date is {{currentDate}}.
