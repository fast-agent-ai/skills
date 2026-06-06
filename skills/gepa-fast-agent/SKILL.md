---
name: gepa-fast-agent
description: Build, review, or refactor GEPA optimization loops that use fast-agent. Use when Codex needs to design GEPA evaluators, Actionable Side Information, Pareto/frontier metrics, FastAgentReflectionLM, FastAgentBatchEvaluator, BatchRunner, EvalRun/CandidateRun artifact layouts, Trackio monitoring, or refactor OpenClaw/Birch-style prompt, policy, skill, batch, or artifact-generation optimizers.
---

# GEPA Fast-Agent

Use this skill to turn a candidate-evaluation problem into a small, auditable GEPA loop backed by fast-agent primitives.

## Core Shape

Think in this order:

1. Candidate: the mutable text GEPA can change, usually a prompt, policy, AgentCard variable, skill file, recipe, or code/config fragment.
2. Evidence: rows, artifacts, logs, screenshots, checker reports, telemetry, usage, traces, or command output produced by evaluating the candidate.
3. Score plus ASI: a numeric score and Actionable Side Information explaining why the candidate passed or failed.

GEPA consumes:

```python
score, side_info = evaluator(candidate)
```

or, in dataset mode, per-example evaluation. Keep GEPA plumbing thin; put reusable execution and artifact capture in fast-agent primitives.

## Non-Negotiable Frontier Rule

GEPA treats scores as maximize-only.

- The main evaluator `score` must be "higher is better".
- Every value in `side_info["scores"]` must also be "higher is better".
- Do not put raw loss, raw latency, raw cost, failure count, error count, timeout seconds, token count, or policy length into `side_info["scores"]` unless transformed so higher is better.
- Keep raw lower-is-better diagnostics outside `side_info["scores"]`, for example under `details`, `raw_metrics`, `summary`, or `failures`.
- Name transformed metrics clearly: `latency_score`, `cost_score`, `valid_json_rate`, `no_timeout`, `policy_length_compliance`, `failure_free_rate`.
- Before running GEPA, audit all frontier keys and write down the transform for each one.

Examples:

```python
side_info = {
    "scores": {
        "accuracy": accuracy,
        "latency_score": 1.0 / (1.0 + latency_seconds),
        "cost_score": 1.0 / (1.0 + dollars),
        "failure_free_rate": 1.0 - failure_count / max(total, 1),
    },
    "raw_metrics": {
        "latency_seconds": latency_seconds,
        "dollars": dollars,
        "failure_count": failure_count,
    },
}
return accuracy, side_info
```

If unsure, check the installed GEPA package source or upstream GEPA docs before
deciding. Search for `higher is better`, `SideInfo`, `scores`, `Pareto`, and
frontier candidate selection.

## Choose The Fast-Agent Primitive

Use `BatchRunner` for row-oriented tasks:

```python
from fast_agent.batch import BatchRunner

runner = BatchRunner(env_dir=".fast-agent", backend="process")
result = await runner.run(
    agent_card=".fast-agent/agent-cards/classifier.md",
    agent="classifier",
    input="eval/input.jsonl",
    template_source="eval/task-template.md",
    json_schema="eval/output.schema.json",
    variables={"policy": candidate["policy"]},
    output_path=candidate_run.path / "results.jsonl",
    summary_path=candidate_run.path / "batch-summary.json",
    telemetry_path=candidate_run.path / "telemetry.jsonl",
    overwrite=True,
)
```

Use `FastAgentBatchEvaluator` when the GEPA evaluator is mostly row/batch execution plus a scorer:

```python
from fast_agent.integrations.gepa import FastAgentBatchEvaluator

evaluator = FastAgentBatchEvaluator(
    env_dir=".fast-agent",
    agent_card=".fast-agent/agent-cards/classifier.md",
    agent="classifier",
    candidate_variables={"policy": "policy"},
    input="eval/input.jsonl",
    template_source="eval/task-template.md",
    schema="eval/output.schema.json",
    scorer=score_candidate,
    run_dir="runs/gepa",
    backend="process",
)
```

Use `EvalRun` / `CandidateRun` for artifact tasks:

```python
from fast_agent.eval import EvalRun

run = EvalRun("runs/gepa")
candidate_run = run.candidate()
candidate_run.materialize_candidate(candidate)
command = candidate_run.run_command(
    ["uv", "run", "python", "scripts/run_eval.py", "--candidate", str(candidate_run.path)],
    timeout_seconds=900,
    log_prefix="eval",
)
candidate_run.write_score(score_value, side_info, metadata={"ok": command.ok})
return score_value, side_info
```

Use `FastAgentReflectionLM` when GEPA reflection should use fast-agent model aliases/config and leave an audit trail:

```python
from fast_agent.integrations.gepa import FastAgentReflectionLM

reflection_lm = FastAgentReflectionLM(
    env_dir=".fast-agent",
    model="responses.gpt-5.5?reasoning=high",
    audit_dir=run_dir / "reflection",
)
```

The reflection adapter should write prompt, request, response, timing, stdout/stderr for process runs, errors, and usage when `--results` contains fast-agent usage channels.

## Trackio Monitoring

For long GEPA runs, add Trackio logging in the evaluator script so candidate
scores and diagnostics are visible while the optimizer is running:

```python
import trackio

trackio.init(project="gepa-openclaw", config={"split": "validation"})

# In a FastAgentBatchEvaluator scorer, candidate_run is available.
score, side_info = score_candidate(result, candidate, candidate_run)
trackio.log(
    {
        "score": score,
        **side_info.get("scores", {}),
        "candidate_index": candidate_run.index or 0,
    }
)
```

Trackio is for monitoring and retrieval, not GEPA frontier semantics. It is
fine to log raw latency, token count, cost, failure count, or artifact size to
Trackio, but do not copy those raw lower-is-better values into
`side_info["scores"]`; transform them first or keep them under `raw_metrics`,
`summary`, or `details`.

When running detached or remote jobs, use a Trackio Space via `space_id` and
poll with CLI JSON output such as `trackio list alerts --project <name> --json`
or `trackio get metric --project <name> --run <run> --metric score --json`.
Use `trackio.alert()` for stalled runs, repeated invalid outputs, failing
smoke checks, or score regressions that should interrupt an autonomous loop.

## Demo Card Pack

When the GEPA demo pack is available in the configured card-pack registry, use it
as a quick smoke test for the evaluator shape it ships:

```bash
fast-agent go --pack gepa-demo
uv run .fast-agent/scripts/gepa-run.py --evaluate-only
```

Keep pack examples aligned with this skill:

- batch demo: AgentCard `variables`, `FastAgentBatchEvaluator`, `FastAgentReflectionLM`;
- artifact demo, when present: `EvalRun`, `CandidateRun`, checker reports, and `write_score`;
- all `side_info["scores"]` values higher-is-better;
- Trackio logging optional and separate from GEPA frontier semantics.

## AgentCard Variables

For mutable prompts/policies, prefer declared AgentCard variables over rendering a new card per candidate:

```markdown
---
type: agent
name: openclaw_classifier
model: "$system.default"
variables:
  policy: ""
---

{{file:eval/openclaw/allowed-topics.md}}

{{policy}}
```

Populate variables per run:

```python
variables={"policy": candidate["policy"]}
```

For CLI smoke tests:

```bash
fast-agent batch run \
  --agent-card .fast-agent/agent-cards/classifier.md \
  --agent classifier \
  --input eval/input.jsonl \
  --output runs/candidate-0001/results.jsonl \
  --template eval/task-template.md \
  --json-schema eval/output.schema.json \
  --var-file policy=seed/policy.md \
  --overwrite \
  --no-final-summary
```

## Scorer Pattern

Keep scoring user-owned and explicit:

1. Read normalized evidence: `BatchRunResult.rows`, `CandidateRun` reports, checker JSON, telemetry, logs, screenshots.
2. Compute one main maximize score.
3. Build ASI with concrete failure examples and repair guidance.
4. Put only maximize metrics in `side_info["scores"]`.
5. Write raw diagnostics outside `scores`.
6. Persist `score.json` through `CandidateRun.write_score()` or the evaluator wrapper.

Good ASI includes:

- exact row/artifact IDs;
- expected vs actual;
- failure categories;
- stderr/stdout tails;
- checker findings;
- screenshots or `gepa.Image` where useful;
- concise actionable feedback;
- raw metrics and transformed frontier metrics.

Avoid ASI that only says "bad" or only returns aggregate numbers; GEPA needs the why.

## Backend Choice

- Use `backend="harness"` for lower overhead in library/API contexts.
- Use `backend="process"` for optimizer loops that need isolation, natural stdout/stderr audit, timeouts, and CLI parity.
- Both backends should return the same structured result/artifact contract.

## OpenClaw Pattern

Use for row/batch classification:

- static AgentCard with declared `policy`;
- `FastAgentBatchEvaluator` with `candidate_variables={"policy": "policy"}`;
- scorer reads `results.jsonl`, summary, telemetry;
- ASI reports confusion, false positives/negatives, invalid JSON, representative failures, and boundary guidance;
- transform policy length, latency, failure count, or cost into maximize scores before adding to `side_info["scores"]`.

## Birch Pattern

Use for artifact-generation evals:

- candidate contains `SKILL.md` and recipe files;
- `EvalRun` allocates candidate dirs;
- `CandidateRun` materializes isolated skill/resource trees;
- `CandidateRun.run_command()` executes generation/checker scripts with timeout;
- reports include artifacts, screenshots, checker JSON/Markdown, stdout/stderr, optional VLM findings;
- scorer owns all weights and penalties, but all frontier keys remain higher-is-better.

## Final Checklist

Before running a long GEPA job:

- Candidate mutation is limited to intended text fields.
- Candidate dirs contain `candidate.json`, variables or materialized files, evidence artifacts, logs, and `score.json`.
- Reflection calls are audited.
- Evaluator can run in `--evaluate-only` or smoke mode.
- All `side_info["scores"]` keys are higher-is-better.
- Raw lower-is-better values are stored outside `scores`.
- The main score is higher-is-better.
- The seed candidate and data split are frozen.
- Lint/typecheck/tests or smoke commands for changed repos have passed.
