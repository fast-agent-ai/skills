# Shared LSP Scaffold

Use this shared scaffold when drafting agent-card or tool-card instructions for LSP-enabled projects. Keep it short and refer to language-specific notes as needed.

## Minimal LSP Context Block

Add a short block explaining the repo layout and how LSP is configured. Prefer `{{fileSilent:pyproject.toml}}` or `{{fileSilent:tsconfig.json}}` so the agent can infer module paths and settings.

Example:

```markdown
This repo uses a standard `src/` layout. The language server is already configured for the workspace root.
{{fileSilent:pyproject.toml}}
```

## Navigation Tooling Guidance

- Prefer direct LSP function tools (hover/definition/references/symbols/diagnostics).
- Add a search sub-agent (ripgrep) only for broad text discovery.
- Avoid a combined mega-tool unless you need a single high-latency “do everything” entry point.

## Repo Layout Checklist

- Root config file present (`pyproject.toml` or `tsconfig.json`).
- `src/` and `tests/` directories clearly defined.
- Dependencies installed in the active environment.

