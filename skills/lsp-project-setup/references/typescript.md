# TypeScript Scaffold

Use this guidance for TypeScript projects using typescript-language-server.

## Minimal Guidance

- Confirm the workspace root is the repo root.
- Ensure `tsconfig.json` is present and reflects the repo layout.
- Keep diagnostics to open files only if performance is a concern.

## Optional Agent-Card Snippet

```markdown
TypeScript LSP: typescript-language-server is configured for the repo root.
{{fileSilent:tsconfig.json}}
```

## Tool-Card Notes

- Prefer direct LSP functions for hover/definition/references/symbols/diagnostics.
- Add search tooling only when broad text discovery is required.

