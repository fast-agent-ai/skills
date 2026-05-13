# Template: Module Explainer

Use this when the user asks to explain a module, subsystem, request path, runtime flow, or part of a codebase.

## User Prompt

Create a standalone Birchline HTML artifact that explains:

`[MODULE_OR_FLOW_NAME]`

Audience:

`[WHO_IS_READING_THIS_AND_WHY]`

Primary question to answer:

`[WHAT_SHOULD_THEY_UNDERSTAND_BY_THE_END]`

Source material:

- Repository/path: `[REPO_OR_PATH]`
- Entry points to inspect: `[FILES_OR_COMMANDS]`
- Known related files: `[OPTIONAL_FILES]`
- Scope boundary: `[RUNTIME_ONLY | MANAGEMENT_FLOWS_TOO | API_ONLY | UI_ONLY | OTHER]`
- Desired depth: `[DIAGRAM_FIRST_OVERVIEW | MAINTAINER_GUIDE | IMPLEMENTATION_CHANGE_GUIDE]`
- Constraints or things to avoid: `[OPTIONAL_CONSTRAINTS]`

## Artifact Recipe

Use the packaged module/code-path explainer recipe. Prioritize the mental model,
runtime path, important files, boundaries, and gotchas.

Recommended sections:

1. Hero: module name, one-sentence thesis, short context.
2. TL;DR: the smallest accurate mental model.
3. Request/data/control path: diagram or step matrix.
4. File tour: important files ordered by reading path, not alphabetically.
5. Key boundary: where trust, state, persistence, IO, or API ownership changes.
6. Known vs inferred: which claims are directly supported by code/tests and which are reasoned from flow.
7. Gotchas: non-obvious behavior, failure modes, or places maintainers get confused.
8. Tests as evidence: tests that confirm important intended behavior, if available.
9. Where to change it: practical guidance for common edits.

## Required Behavior

- Inspect the relevant code before writing the artifact.
- Cite concrete file paths and functions/classes where useful.
- Prefer diagrams, timelines, code panels, and matrices over long prose.
- Mark uncertain inferences clearly.
- If scope is ambiguous, choose a reasonable default and label what you excluded.
- Keep the generated HTML standalone and embed only Birchline Core + Components.
