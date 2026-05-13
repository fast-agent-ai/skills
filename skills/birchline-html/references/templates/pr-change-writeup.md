# Template: PR / Change Writeup

Use this when the user wants a reviewer-facing explanation of a pull request, patch, branch, diff, migration, or code change.

## User Prompt

Create a standalone Birchline HTML writeup for this change:

`[PR_BRANCH_OR_CHANGE_NAME]`

Audience:

`[REVIEWERS_OR_STAKEHOLDERS]`

Source material:

- Diff or branch: `[DIFF_BRANCH_PR_URL_OR_LOCAL_RANGE]`
- Motivation: `[WHY_THIS_CHANGE_EXISTS]`
- Areas reviewers may not know: `[CONTEXT_GAPS]`
- Rollout constraints: `[FLAGS_MIGRATIONS_RELEASE_NOTES]`

## Artifact Recipe

Use the packaged PR/change-writeup recipe. Explain the change for reviewers and
stakeholders, with enough evidence to make review efficient.

Recommended sections:

1. Hero: PR/change name, metadata, review goal.
2. TL;DR: what changed and why it matters.
3. Before/after: behavior, architecture, performance, or UX.
4. File-by-file tour: reading order, why each file changed, what to focus on.
5. Review focus: exactly where reviewers should spend attention.
6. Tests and evidence: commands run, screenshots, metrics, fixtures.
7. Rollout and rollback: flags, migrations, monitoring, fallback path.
8. Open questions: unresolved choices or follow-up work.

## Required Behavior

- Inspect the diff or branch before writing.
- Order files by reviewer comprehension, not alphabetically.
- Keep code snippets short and purposeful.
- Avoid marketing language; this is a practical reviewer artifact.
- Keep the generated HTML standalone and embed only Birchline Core + Components.
