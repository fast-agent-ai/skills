# Template: Slide Deck

Use this when the user wants a compact briefing deck, weekly update, decision
readout, roadmap narrative, executive summary, or presentation-style artifact.

## User Prompt

Create a standalone Birchline HTML slide-deck artifact for:

`[DECK_TOPIC]`

Audience:

`[WHO_WILL_READ_OR_PRESENT_THIS]`

Narrative goal:

`[UPDATE | DECISION | PROPOSAL | RETROSPECTIVE | HANDOFF | OTHER]`

Source material:

- Notes/data/files: `[SOURCES]`
- Time window: `[DATES_OR_PERIOD]`
- Required slides: `[OPTIONAL_SLIDE_LIST]`
- Key decision or ask: `[DECISION_OR_ASK]`
- Constraints: `[PRINTABLE | SCROLLABLE | EXECUTIVE_BRIEF | TECHNICAL_DEEP_DIVE | OTHER]`

## Artifact Recipe

Use the packaged slide/deck recipe derived from the original slide deck source
example. Build a scrollable sequence of slide-like sections, not a marketing
landing page.

Recommended sections:

1. Title slide: topic, date/window, presenter/source, slide count.
2. Executive summary: 3-5 takeaways.
3. What shipped or changed: concrete delivered items with refs.
4. In progress: work carrying forward, confidence, blockers, owners.
5. Metrics: exact numbers with short trend/delta context.
6. Decision or ask: one clear choice, tradeoffs, and recommended path.
7. Next period: commitments, watch items, and follow-ups.

## Visual Guidance

- Use full-width slide bands or tall sections with generous whitespace.
- Keep each slide to one job; avoid dense dashboard pages pretending to be
  slides.
- Use stat strips, progress bars, short lists, and decision cards.
- For numeric slides, use `numeric-data.md` guidance and Matplotlib SVG when
  plotting real data.
- Ensure the deck works as a local HTML page and remains readable when printed.

## Required Behavior

- Preserve chronology and dates when source material provides them.
- Do not invent metrics, shipped items, or decisions.
- Make the decision/ask visible before the end if it is the reason for the deck.
- Keep the generated HTML standalone and embed only Birchline Core + Components.
