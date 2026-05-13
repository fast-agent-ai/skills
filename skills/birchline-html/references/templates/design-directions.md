# Template: Design Directions

Use this when the user wants multiple possible UI, architecture, API, workflow, or product directions before choosing one.

## User Prompt

Create a standalone Birchline HTML artifact comparing design directions for:

`[PROBLEM_OR_SURFACE]`

Decision needed:

`[WHAT_CHOICE_MUST_BE_MADE]`

Context:

- Current state: `[CURRENT_STATE]`
- Users/readers affected: `[AUDIENCE]`
- Constraints: `[TECH_PRODUCT_DESIGN_CONSTRAINTS]`
- Options already in mind: `[OPTIONAL_OPTIONS]`
- Evaluation criteria: `[CRITERIA]`

## Artifact Recipe

Use the packaged design-directions recipe. Compare genuinely distinct options
against clear criteria and make the recommendation easy to scan.

Recommended sections:

1. Hero: problem, decision, recommendation if known.
2. Evaluation criteria: what makes an option good or bad.
3. Direction cards: 3-4 options with thesis, shape, strengths, weaknesses.
4. Comparison matrix: options against criteria.
5. Recommendation: chosen path, why, and what would change the decision.
6. Next experiment: smallest prototype or proof point to run.

## Required Behavior

- Make options genuinely distinct, not superficial variants.
- Avoid pretending all options are equally good if one is clearly stronger.
- Call out tradeoffs in product, engineering, user experience, and maintenance terms.
- Keep the generated HTML standalone and embed only Birchline Core + Components.
