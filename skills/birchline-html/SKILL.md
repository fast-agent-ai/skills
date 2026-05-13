---
name: birchline-html
description: Create polished standalone single-file HTML engineering artifacts in the Birchline design language. Use for session summaries, module/process explainers, implementation plans, design direction comparisons, PR/change writeups, findings-first code reviews, incident/status reports, slide decks, flow diagrams, and compact numeric/data briefs where the output should be a beautiful local HTML document with embedded CSS and no external assets.
metadata:
  short-description: Standalone Birchline HTML artifacts
---

# Birchline HTML

Use this skill when the user wants a beautiful standalone HTML artifact, report,
summary, explainer, plan, or dashboard in the Birchline visual language.

The goal is a single `.html` file that opens locally, embeds all CSS, uses no
network resources, and reads like a serious engineering artifact rather than a
generic web page.

## Workflow

1. Gather the source facts first.
   Read files, session notes, data, diffs, commands, and screenshots as needed.
   Do not ask the renderer/layout phase to discover facts that the calling agent
   can already provide.

2. Build a renderer brief.
   Make it self-contained: audience, purpose, known facts, evidence, file paths,
   commands, data values, caveats, unknowns, suggested sections, and chart intent.
   Mark uncertain details as unknown instead of inventing them.

3. Choose an artifact type.
   Use the nearest recipe from `references/templates/`:
   - `module-explainer.md`
   - `process-explainer.md`
   - `implementation-plan.md`
   - `design-directions.md`
   - `code-review.md`
   - `pr-change-writeup.md`
   - `status-or-incident-report.md`
   - `slide-deck.md`
   - `flow-diagram.md`
   - `numeric-data.md`

4. Write one complete standalone HTML document.
   Start from `assets/templates/standalone-shell.html` if useful. Inline both:
   - `assets/birchline-core.css`
   - `assets/birchline-components.css`

5. Validate before finishing.
   Check that the file has `<!doctype html>`, `<style>`, `<body>`, closing
   `</html>`, no external scripts/styles/fonts, and responsive layouts for
   tables or wide content. If possible, render a desktop and mobile screenshot.

## Birchline Rules

- Use ivory/paper backgrounds, slate text, restrained clay accents, serif display
  headings, and quiet sans/mono supporting text.
- Favor sections, panels, matrices, stat strips, timelines, code panels, badges,
  callouts, and comparison grids.
- Keep cards for repeated items, modals, or framed tools. Avoid nested cards.
- Do not use generic gradient blobs, decorative orbs, stock imagery, CDN fonts,
  external CSS, or JavaScript unless the user explicitly needs interaction.
- Keep first viewport useful: title, purpose, status/caveat, and strongest facts.
- Wrap long paths and symbols aggressively; prefer matrices or code panels over
  dense paragraphs.
- Exact values should appear as text near charts, not only as shape height/width.
- For large source material, produce a shorter complete artifact rather than an
  ambitious incomplete one.

## Numeric/Data Guidance

For arbitrary data, inspect the shape before choosing the visualization:

- KPI strip: headline counts, totals, best/worst, pass/fail, cost/time.
- Delta card: before/after or baseline/current comparisons.
- Ranking bars: sorted categories with exact values.
- Grouped bars: compare the same measures across a few categories.
- Progression line: ordered/time progression.
- Small multiples: repeated mini charts for multiple entities.
- Comparison matrix: exact values, statuses, or tradeoffs.
- Distribution strip: spread, range, buckets, or concentration.
- Annotated table: when exact reading matters more than visual drama.

Use CSS or hand-written inline SVG only for tiny charts, simple bars, sparklines,
or diagram-like marks. For plotted numeric data, default to Python-generated SVG
so axes, ticks, labels, scales, legends, and statistical views are handled
reliably. Avoid fitting the design to one fixed data schema; choose the simplest
honest view for the supplied data.

For charts, prefer this route:

1. Use Matplotlib as the default renderer for real plotted data. Use Seaborn
   when it makes a distribution, regression, heatmap, or grouped statistical
   view clearer without fighting the Birchline theme.
2. Use the bundled helper `scripts/birchline_mpl.py` for theme and SVG export.
   Create a temporary or artifact-local driver script that imports or copies that
   helper, loads the specific data, builds the figure, and writes the SVG/HTML.
   Run the driver with `uv`, for example:
   `uv run --with matplotlib --with numpy python /tmp/build_chart.py`
   or, when useful:
   `uv run --with matplotlib --with seaborn --with pandas python /tmp/build_chart.py`.
3. Export SVG and inline it into the HTML inside a `.panel` or chart container.
4. Pair the chart with exact values in a numeric table/matrix and a source/caveat
   note.
5. Use PNG only for raster-heavy plots where SVG is impractical.

## Reference Loading

Only load extra references when needed:

- Read `references/system.md` for the canonical full design-system prompt.
- Read `references/patterns.md` for detailed component and layout patterns.
- Read `references/recipe-catalog.md` when choosing among packaged recipes or
  checking known gaps.
- Read a specific file in `references/templates/` when the artifact type is clear.
- Read or reuse `scripts/birchline_mpl.py` when generating Matplotlib charts.

## Slash Command Alternative

If working inside the fast-agent environment that has the Birchline plugin
installed, prefer `/birchline` when the user wants automated generation from
session context. Use this skill when you want the current agent to create or edit
the artifact directly.
