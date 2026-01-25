---
name: lsp-project-setup
description: Create or update LSP-ready project scaffolds and agent-card guidance for Python or TypeScript repos. Use when configuring tool cards or agent cards to navigate a codebase with LSP (ty, typescript-language-server), including workspace roots, venvs, and minimal project config references.
---

# LSP Project Setup

Provide concise scaffolding for LSP-ready projects. Keep tool cards minimal unless the repo needs special handling.

## Output Location

Agent cards **must** be placed in `.fast-agent/agent-cards/`, not directly in `.fast-agent/`.

Example paths:
- Agent card: `.fast-agent/agent-cards/my-agent.yaml`
- Tool card: `.fast-agent/tool-cards/my-tool.yaml`

## Standard Flow

1. Confirm the workspace root (repo root).
2. Confirm the language server (ty for Python, typescript-language-server for TS).
3. Confirm the active environment/venv and dependency install strategy.
4. Create the agent card in `.fast-agent/agent-cards/`.
5. Add a minimal scaffold with `{{fileSilent:pyproject.toml}}` or `{{fileSilent:tsconfig.json}}` context.
6. Add optional diagnostic tuning only when needed.

## Shared Scaffold

Load [references/shared.md](references/shared.md) for the shared scaffolding text and layout guidance.

## Language-Specific Guidance

- Python + ty: Load [references/python.md](references/python.md).
- TypeScript: Load [references/typescript.md](references/typescript.md).
