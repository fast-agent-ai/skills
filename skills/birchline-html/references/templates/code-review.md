# Template: Findings-First Code Review

Use this when the user wants a review artifact, not just a PR explanation:
bugs, regressions, risks, missing tests, suspicious diffs, or reviewer guidance.

## User Prompt

Create a standalone Birchline HTML code-review artifact for:

`[PR_BRANCH_DIFF_OR_CHANGE]`

Review goal:

`[WHAT_RISK_SHOULD_BE_FOUND_OR_DECIDED]`

Source material:

- Repository/path: `[REPO_OR_PATH]`
- Diff/branch/range: `[DIFF_BRANCH_PR_URL_OR_LOCAL_RANGE]`
- Areas of concern: `[OPTIONAL_AREAS]`
- Test evidence: `[COMMANDS_LOGS_CI_SCREENSHOTS]`
- Review posture: `[BLOCKING_FINDINGS | RISK_MAP | HANDOFF_FOR_REVIEWERS | OTHER]`

## Artifact Recipe

Use the packaged findings-first review recipe. This is different from
`pr-change-writeup.md`: lead with risks and actionable findings, not with a
promotional change narrative.

Recommended sections:

1. Hero: change name, review scope, verdict or current risk state.
2. Findings first: ordered by severity, with file/function/line references.
3. Risk map: files or surfaces grouped by needs-attention / worth-a-look / low-risk.
4. Diff tour: only the files needed to understand the findings.
5. Evidence: tests, logs, screenshots, reproduction notes, or missing evidence.
6. Reviewer checklist: concrete questions or lines to inspect.
7. Residual risk: what remains uncertain after this review.

## Required Behavior

- Inspect the diff before writing.
- Do not bury blocking findings below summaries.
- Include no findings section if no actionable issue is found, and then state
  residual risk or test gaps.
- Keep snippets short and wrap long code/paths.
- Keep the generated HTML standalone and embed only Birchline Core + Components.
