# Template: Implementation Plan

Use this when the user asks how to build, change, migrate, refactor, or add a feature.

## User Prompt

Create a standalone Birchline HTML implementation plan for:

`[CHANGE_OR_FEATURE]`

Goal:

`[WHAT_SUCCESS_LOOKS_LIKE]`

Context:

- Repository/path: `[REPO_OR_PATH]`
- Current behavior: `[CURRENT_BEHAVIOR]`
- Desired behavior: `[DESIRED_BEHAVIOR]`
- Likely files/packages: `[FILES_OR_PACKAGES]`
- Interface contract: `[CLI_FLAGS_EXIT_CODES | API_SCHEMA | UI_STATES | CONFIG_SCHEMA | OTHER]`
- Surface parity: `[CLI_ONLY | UI_ONLY | SLASH_COMMAND_TOO | API_AND_UI | OTHER]`
- Diagnostic or feature scope: `[LOCAL_ONLY | NETWORK_ALLOWED | READ_ONLY | WRITES_ALLOWED | OTHER]`
- Constraints: `[COMPATIBILITY_TESTING_ROLLOUT_CONSTRAINTS]`
- Non-goals: `[WHAT_NOT_TO_CHANGE]`

## Artifact Recipe

Use the packaged implementation-plan recipe. Make the plan concrete enough that
an implementer can start from it without rereading the entire source context.

Recommended sections:

1. Hero: feature/change name, goal, scope badges.
2. Executive summary: effort, surfaces touched, feature flags, migration needs.
3. Milestones: reviewable slices in implementation order.
4. Data/control flow: diagram or matrix from UI/API/runtime to persistence/side effects.
5. Interface shape: UI, CLI, API, config, schema, or command contract.
6. Key code: files/classes/functions to edit and why.
7. Confirmed vs assumed: what the repo/source proves, and what the plan infers.
8. Tests and verification: unit, integration, manual, visual, migration checks.
9. Risks and mitigations: concrete risks with owners or guardrails.
10. Open questions: decisions that must be answered before or during build.

## Required Behavior

- Inspect the codebase where available before proposing edits.
- Separate confirmed facts from assumptions.
- Prefer a conservative plan that matches existing architecture.
- Specify interface details such as flags, output format, exit codes, API contract, or UI states when relevant.
- If scope is ambiguous, choose a v1 scope and put excluded work in non-goals or open questions.
- Include enough detail that an implementer can start without rereading the whole repo.
- Keep the generated HTML standalone and embed only Birchline Core + Components.
