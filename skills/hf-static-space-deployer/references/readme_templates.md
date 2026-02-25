# README templates for Static Spaces

Use one of these at repo root as `README.md`.

## Template A: Plain static site (no build step)

```yaml
---
title: My Static Site
emoji: 🌐
colorFrom: blue
colorTo: indigo
sdk: static
app_file: index.html
pinned: false
---
```

Notes:
- Commit `index.html` (and all referenced assets) directly to the repo.

---

## Template B: Built frontend app (Vite/React/Svelte/Vue)

```yaml
---
title: My Frontend App
emoji: ⚡
colorFrom: purple
colorTo: blue
sdk: static
app_build_command: npm run build
app_file: dist/index.html
pinned: false
---
```

Notes:
- `app_build_command` runs on each update.
- `app_file` must point to built HTML output.
- If your framework outputs elsewhere, change `app_file` (for example `build/index.html`).

---

## Optional metadata fields commonly used

Add as needed:

- `short_description`
- `fullWidth`
- `header`
- `thumbnail`
- `tags`
- `models`
- `datasets`
- `disable_embedding`
- `custom_headers`
