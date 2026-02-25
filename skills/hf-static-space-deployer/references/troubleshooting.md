# Troubleshooting Static Spaces

## Build fails immediately

Check:
1. `README.md` YAML is valid.
2. `sdk: static` is set.
3. `app_build_command` is correct for project scripts.

Fix:
- Run build locally first.
- Ensure lockfile/package manager assumptions are consistent.

---

## Space builds but shows blank/404 app

Check:
1. `app_file` points to real built file.
2. Output folder matches framework config.
3. Asset paths are correct (absolute vs relative).

Fix:
- Update `app_file` path in README metadata.
- Use correct public/base path config for frontend bundler.

---

## CSS/JS assets 404 after deploy

Check:
- App uses root-absolute paths that do not match served structure.
- Build tool base/public path settings.

Fix:
- Configure framework base path appropriately.
- Rebuild and redeploy.

---

## SPA route reload returns 404-like behavior

Cause:
- Static hosting often lacks server-side history fallback.

Fix options:
1. Use hash-based routing.
2. Add framework-specific static fallback strategy if available.
3. Prefer routes that can be loaded from built static artifact layout.

---

## Query/hash in parent Space URL not syncing as expected

Cause:
- Spaces embeds app in an iframe and only propagates parent params on initial load.

Fix:
- Use `window.parent.postMessage({ queryString, hash }, "https://huggingface.co")` when you need to update parent URL state.

---

## Variable/secret handling confusion in static app

Important:
- In static Spaces, variables are accessible from frontend JS via `window.huggingface.variables`.

Fix:
- Do not store sensitive secrets that must remain server-only in a static frontend architecture.
- Move sensitive logic to a backend (for example Docker Space API service) if required.
