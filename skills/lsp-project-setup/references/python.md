# Python (ty) Scaffold

Use this guidance when the repo uses ty as the Python language server.

## Minimal Guidance

- Confirm the workspace root is the repo root.
- Ensure the active interpreter/venv has dependencies installed (ty resolves imports from that env).
- Keep diagnostics to `openFilesOnly` for large repos when the editor supports it.

## Optional Agent-Card Snippet

```markdown
Python LSP: ty is configured for the repo root. Dependencies resolve from the active venv.
{{fileSilent:pyproject.toml}}
```

## Tool-Card Notes

- Use direct LSP functions for hover/definition/references/symbols/diagnostics.
- Add ripgrep search only if you expect broad text discovery beyond LSP.

