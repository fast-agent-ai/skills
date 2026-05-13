# Template: Status or Incident Report

Use this when the user wants to summarize current project status, an incident, a reliability issue, an investigation, or a recovery plan.

## User Prompt

Create a standalone Birchline HTML report for:

`[STATUS_OR_INCIDENT_NAME]`

Report type:

`[STATUS_REPORT | INCIDENT_REPORT | INVESTIGATION | RETROSPECTIVE]`

Source material:

- Logs/notes/tickets/PRs: `[SOURCES]`
- Time window: `[DATES_OR_TIMES]`
- Impact or audience: `[IMPACT]`
- Current state: `[CURRENT_STATE]`
- Known next actions: `[NEXT_ACTIONS]`

## Artifact Recipe

Use the packaged status/incident recipe. Make current state, impact, timeline,
actions, and remaining risk obvious.

Recommended sections:

1. Hero: status/incident name, severity or confidence, current state.
2. Summary stats: impact, duration, affected surfaces, remaining risk.
3. Timeline: key events in chronological order.
4. What happened / where things stand: concise narrative.
5. Root cause or drivers: use confidence labels if not fully proven.
6. Actions: done, in progress, next, owner/status.
7. Risks and watch items: what could still go wrong.
8. Follow-ups: durable fixes, docs, tests, monitoring, owners.

## Required Behavior

- Use absolute dates/times if the source includes relative time.
- Do not overclaim root cause; distinguish evidence from inference.
- Make the current state obvious in the first viewport.
- Keep the generated HTML standalone and embed only Birchline Core + Components.
