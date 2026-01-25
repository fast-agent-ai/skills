---
name: lsp-project-setup
description: Create or update LSP-ready project scaffolds and agent-card guidance for Python or TypeScript repos. Use when configuring tool cards or agent cards to navigate a codebase with LSP (ty, typescript-language-server), including workspace roots, venvs, and minimal project config references.
---

# LSP Project Setup

Provide concise scaffolding for LSP-ready projects. Keep tool cards minimal unless the repo needs special handling.

## Output Location

Agent cards **must** be placed in `.fast-agent/agent-cards/`, not directly in `.fast-agent/`.

Example paths:
- Agent card: `.fast-agent/agent-cards/dev.md`
- Tool card: `.fast-agent/tool-cards/my-tool.yaml`

## Standard Flow

1. Confirm the workspace root (repo root).
2. Confirm the language server (ty for Python, typescript-language-server for TS).
3. Confirm the active environment/venv and dependency install strategy.
4. Create the agent card in `.fast-agent/agent-cards/` using the appropriate example.
5. Copy required tool files (e.g., `multilspy_tools.py`) alongside the card.
6. Add optional diagnostic tuning only when needed.

## Example Cards

- Python + ty: Load [references/python-card-example.md](references/python-card-example.md) for a complete agent card.
- TypeScript: Load [references/typescript-card-example.md](references/typescript-card-example.md) for a complete agent card.
- Shared instructions: Load [references/lsp-dev-shared.md](references/lsp-dev-shared.md) for reusable instruction blocks.

## Language-Specific Setup Notes

- Python + ty: See [references/python.md](references/python.md) for environment and diagnostic guidance.
- TypeScript: See [references/typescript.md](references/typescript.md) for tsconfig and diagnostic guidance.
