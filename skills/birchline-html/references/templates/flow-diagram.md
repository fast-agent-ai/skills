# Template: Flow Diagram

Use this when the user wants a deploy path, request lifecycle, state machine,
workflow, dependency chain, decision tree, or annotated technical process drawn
as a diagram.

## User Prompt

Create a standalone Birchline HTML flow-diagram artifact for:

`[FLOW_OR_PROCESS_NAME]`

Primary question:

`[WHAT_THE_READER_SHOULD_UNDERSTAND]`

Source material:

- Repository/path or docs: `[REPO_DOCS_OR_NOTES]`
- Entry points/configs: `[FILES_COMMANDS_WORKFLOWS]`
- States/steps/gates: `[KNOWN_STEPS]`
- Failure paths: `[KNOWN_FAILURE_ROLLBACK_OR_ESCALATION_PATHS]`
- Audience: `[MAINTAINER | REVIEWER | INCIDENT_RESPONDER | STAKEHOLDER | OTHER]`

## Artifact Recipe

Use the packaged flow/diagram recipe. Prefer a clear inline SVG diagram plus
nearby notes over a long textual walkthrough.

Recommended sections:

1. Hero: flow name, trigger, output, and scope.
2. Diagram: inline SVG or structured flow panel with nodes, edges, gates, and
   failure paths.
3. Step notes: short explanations keyed to diagram labels.
4. Evidence map: files, configs, commands, or logs that prove each major step.
5. Failure and rollback paths: what happens when gates fail.
6. Timing/ownership: durations, owners, systems, or handoffs if known.
7. Unknowns: inferred edges or missing instrumentation.

## Visual Guidance

- Use clay for warning/failure paths, olive for success/healthy paths, slate/gray
  for ordinary flow, and oat/ivory surfaces.
- Keep SVG text readable on mobile; allow wide diagrams to scroll when needed.
- Do not create decorative diagrams. Every node should clarify a real transition,
  state, gate, owner, or side effect.

## Required Behavior

- Inspect source files/configs when available before drawing the flow.
- Distinguish confirmed flow from inferred flow.
- Prefer stable labels over dense prose inside the SVG.
- Keep the generated HTML standalone and embed only Birchline Core + Components.
