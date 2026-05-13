# Numeric Data Brief

Use for small metrics reports, evaluation summaries, benchmark comparisons,
dashboard-style briefs, and arbitrary data the user asks to plot or summarize.

## Brief Requirements

- State the source data and any caveats.
- Identify measures, dimensions, groups, order/time fields, denominators, and
  units before choosing charts.
- Include exact values near visuals.
- Prefer the simplest honest chart over decorative complexity.

## Recommended Structure

1. Hero with the key finding and source caveat.
2. KPI strip for headline numbers.
3. One or two focused charts selected from the chart vocabulary.
4. Exact comparison matrix or annotated table.
5. Caveats, missing data, and follow-up questions.

## Chart Vocabulary

- KPI strip
- Delta card
- Ranking bars
- Grouped bars
- Progression line
- Small multiples
- Comparison matrix
- Distribution strip
- Annotated table

Use CSS or hand-written inline SVG only for tiny/simple visuals. For real plotted
numeric data, prefer Python-generated SVG with Matplotlib so axes, ticks, scales,
legends, and labels are reliable. Use Seaborn when it improves distributions,
regressions, heatmaps, or grouped statistical views without fighting the
Birchline theme. Create a temporary or artifact-local chart script, then run it
with `uv`. The script should import or copy the bundled Birchline Matplotlib
helper, `scripts/birchline_mpl.py`, for colors, gridlines, typography, and SVG
export:

```bash
uv run --with matplotlib --with numpy python /tmp/build_chart.py
uv run --with matplotlib --with seaborn --with pandas python /tmp/build_chart.py
```

Inline the exported SVG in the standalone HTML. Avoid external JavaScript
charting libraries unless the user explicitly asks for interaction.

## Numeric Tables

Use the shared numeric table pattern for exact values that accompany charts:

```html
<div class="numeric-table-wrap">
  <table class="numeric-table">
    <thead>
      <tr><th>Entity</th><th>Metric A</th><th>Metric B</th><th>Note</th></tr>
    </thead>
    <tbody>
      <tr>
        <td class="entity">Spark<span class="subtle">renderer</span></td>
        <td class="metric" data-label="metric a">82</td>
        <td class="metric" data-label="metric b">88</td>
        <td class="note">Promising when given a tight renderer brief.</td>
      </tr>
    </tbody>
  </table>
</div>
```

Keep numeric columns right-aligned on desktop and include `data-label` attributes
so the table becomes readable mobile rows.
