# Skills Management Reference

This section captures how skills are discovered and overridden in fast-agent automation.

## Global discovery defaults

By default, fast-agent searches these skill directories:

- `.fast-agent/skills`
- `.agents/skills`
- `.claude/skills`

(From `DEFAULT_SKILLS_PATHS` in `src/fast_agent/constants.py`.)

## CLI override

Use:

- `--skills-dir <path>` (alias: `--skills <path>`)

Available on `fast-agent go` and `fast-agent serve` shared options.

Example:

```bash
fast-agent go \
  --card ./cards \
  --skills-dir ./.fast-agent/skills \
  --model sonnet \
  --message "run" \
  --results out.json
```

### What override means

`--skills-dir` updates settings-backed skill directories used for global skill resolution.

If settings specify explicit skill directories, fast-agent skill manager also ensures the manager
storage directory is included in resolved directories.

## Agent-card `skills` field semantics

In an agent card frontmatter, `skills` controls per-agent skill resolution behavior.

### Omitted `skills`

- Uses sentinel default behavior (`SKILLS_DEFAULT`)
- Agent receives globally discovered skills

### `skills: []`

- Explicitly disables skills for that agent
- Useful for deterministic/tool-constrained cards

### `skills: <string path>` or `skills: ["pathA", "pathB"]`

- Treated as explicit skill directory path(s) for that agent
- Manifests are loaded from those directories

## Prompt-template caveat

Skills are injected through `{{agentSkills}}` template rendering.

- Default agent instruction includes `{{agentSkills}}`
- If a custom instruction omits `{{agentSkills}}`, fast-agent can still have skills configured,
  but the skill list text is not injected into system prompt text

## Automation recommendation

- Prefer explicit `--skills-dir` in CI/jobs when reproducibility matters
- Use `skills: []` for cards that must avoid ambient skills
- Use omitted `skills` for cards that should inherit deployment/site defaults
