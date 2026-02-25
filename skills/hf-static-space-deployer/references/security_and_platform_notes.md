# Security and platform notes for Static Spaces

## Hosting model

- Space page is on `huggingface.co/spaces/<owner>/<name>`.
- App runs from `*.hf.space` in an iframe.
- Browser security behavior (cookies/storage) may differ from first-party single-domain hosting.

## Secret/variable exposure model for static apps

- Static app code runs client-side.
- Static Space variables are available through `window.huggingface.variables`.
- Treat static frontend values as user-visible in threat modeling.

## Network and runtime expectations

- Static apps should not require long-running backend processes.
- If backend compute/runtime is needed, migrate to Docker Space.

## Dev workflow caveat

- Spaces Dev Mode is not available for static Spaces.
- For rapid in-cloud edit/debug loops, Docker Spaces are a better fit.
