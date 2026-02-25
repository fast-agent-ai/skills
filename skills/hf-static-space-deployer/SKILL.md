---
name: hf-static-space-deployer
description: >-
  Deploy general static websites and frontend apps to Hugging Face Spaces using `sdk: static`.
  Use when the user wants to host HTML/CSS/JS sites or built SPA frontends (React, Vite,
  Svelte, Vue, etc.) on Spaces for convenient sharing. Include setup for README YAML metadata
  (`app_file`, optional `app_build_command`), deployment via `hf` CLI or Python API, GitHub
  Actions sync, and static-Space troubleshooting.
---

# HF Static Space Deployer

Deploy static web content to Hugging Face Spaces in a repeatable way.

## Choose the correct deployment mode

Use this skill when the app is static output.

1. **Plain static files** (no build step)
   - `index.html` + CSS/JS files committed directly.
   - Use `sdk: static` and `app_file: index.html`.

2. **Build-first static app**
   - Framework source (React/Vite/Svelte/Vue/etc.) requires build.
   - Use `sdk: static`, `app_build_command`, and `app_file` pointing to built HTML (for example `dist/index.html`).

3. **Do not use this skill** when server-side runtime is required
   - If the app needs a backend process, custom server routes, or non-static runtime behavior, use Docker Spaces instead.

## Minimum required repo structure

At minimum, ensure:

- `README.md` with YAML metadata block (includes `sdk: static`).
- App entry HTML referenced by `app_file`.
- Any source/build files needed for build (if using `app_build_command`).

See templates in:
- [references/readme_templates.md](references/readme_templates.md)

## Standard workflow

1. Authenticate with Hugging Face.
2. Create Space as `repo_type=space` and `space_sdk=static`.
3. Upload project files.
4. Wait for build/startup.
5. Validate app URL and behavior.

Use exact commands from:
- [references/deploy_workflows.md](references/deploy_workflows.md)

## Deployment quality checks

After upload/build, verify:

1. Space build succeeds.
2. `app_file` exists at expected path.
3. Site loads at the Space URL.
4. Asset paths resolve correctly (no broken CSS/JS).
5. If SPA:
   - hash routing works directly; history routing may need fallback strategy.
6. If query/hash syncing with parent page is required, use Spaces postMessage pattern.

See:
- [references/troubleshooting.md](references/troubleshooting.md)

## Security and platform caveats

1. Static Spaces run inside an iframe on `huggingface.co/spaces/...`.
2. For static Spaces, variables/secrets are available to browser JS through `window.huggingface.variables`.
3. Do not treat static frontend variables as confidential server-only secrets.
4. Cookie behavior can differ from first-party hosting due to iframe constraints.

Use:
- [references/security_and_platform_notes.md](references/security_and_platform_notes.md)

## CI/CD guidance

Prefer one of:

1. Push directly with `hf upload`.
2. Mirror from GitHub with a GitHub Action that pushes to the Space repo.

Use templates from:
- [references/deploy_workflows.md](references/deploy_workflows.md)

## Local tooling bundled with this skill

- `scripts/scaffold_static_space.py`: generate a `README.md` metadata block and optional GitHub Action workflow.
- `scripts/validate_static_space.py`: validate local projects and/or existing deployed Spaces (for example `--space-id evalstate/foo`).

## Output expectations

When helping a user, always produce:

1. Final `README.md` YAML block.
2. Exact deploy command sequence.
3. Suggested CI option (manual or GitHub Actions).
4. Post-deploy validation checklist.
5. Troubleshooting steps tailored to framework/output path.
