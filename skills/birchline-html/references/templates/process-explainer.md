# Template: Process Explainer

Use this when the user asks to explain a workflow, operational process, lifecycle, handoff, release path, debugging routine, or team procedure.

## User Prompt

Create a standalone Birchline HTML artifact that explains this process:

`[PROCESS_NAME]`

Audience:

`[WHO_NEEDS_TO_FOLLOW_OR_UNDERSTAND_IT]`

Desired outcome:

`[WHAT_THE_READER_SHOULD_BE_ABLE_TO_DO_AFTER_READING]`

Source material:

- Notes/docs/logs/code paths: `[SOURCES]`
- Actors/systems involved: `[ACTORS_OR_SYSTEMS]`
- Known decision points: `[DECISIONS]`
- Known failure modes: `[FAILURES_OR_EDGE_CASES]`

## Artifact Recipe

Recommended sections:

1. Hero: process name, context, outcome.
2. Operating model: actors, systems, and responsibilities.
3. Lifecycle: timeline, state machine, or step sequence.
4. Decision points: branches, approvals, thresholds, or gates.
5. Failure modes: what breaks, how it appears, how to recover.
6. Checklist: compact action list for someone running the process.
7. Open questions: gaps or policy choices still unresolved.

## Required Behavior

- Use timelines, matrices, stat blocks, and callouts when they make the process easier to follow.
- Avoid generic process advice; ground the page in the provided sources.
- Make mobile layout readable for someone using it during work.
- Keep the generated HTML standalone and embed only Birchline Core + Components.
