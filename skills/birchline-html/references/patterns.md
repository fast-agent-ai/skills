# Birchline HTML generation guide

Use Birchline as a stable design kernel for standalone HTML artifacts. Generated pages should embed the canonical CSS rather than improvising style rules.

## CSS layers

1. `birchline-core.css`
   - tokens
   - body/page defaults
   - heading/type rules
   - section/rule helpers
   - basic grids/utilities
   - compatibility aliases for the original `index.html` (`--paper`, `--g100`, etc.)

2. `birchline-components.css`
   - panels
   - buttons
   - inputs/checkboxes
   - badges/chips
   - card base and card variants
   - stats
   - code panels
   - timelines

3. `birchline-homepage.css`
   - use only for galleries/catalog homepages
   - includes masthead hero figure, TOC pills, demo-card thumbnail grid

## Default page recipe

```html
<div class="page">
  <header class="hero">
    <p class="eyebrow">Concept explainer</p>
    <h1>Explain the idea with one strong sentence</h1>
    <p class="lede">A short, specific introduction that says what the reader will understand by the end.</p>
  </header>

  <section>
    <div class="sec-head"><span class="idx">01</span><h2>Main section</h2></div>
    <p class="sec-intro">A compact framing paragraph.</p>
    <div class="grid auto">
      <article class="card v-outlined">...</article>
      <article class="card v-stripe">...</article>
    </div>
  </section>
</div>
```

## Style rules for the agent

- Always use ivory page background and slate primary text.
- Use serif for headings, sans for body, mono for labels/metadata.
- Prefer `panel`, `card`, `stat`, `timeline`, and `code-panel` primitives over ad hoc boxes.
- Use clay sparingly for primary emphasis, active paths, stripes, and calls to action.
- Use olive for success/healthy/positive states.
- Use gray-500 for secondary text.
- Use `1.5px solid var(--gray-300)` borders, `12px` panels, `8px` controls.
- Keep pages standalone: inline the CSS from the chosen layers into the generated HTML.
- Only include `birchline-homepage.css` for index/gallery/catalog pages.

## Card variants

- `v-flat`: dense lists on tinted backgrounds
- `v-outlined`: default content cards on ivory
- `v-elevated`: popovers, draggable items, prominent floating cards
- `v-stripe`: priority/pinned/highlighted content
- `v-inset`: nested cards inside white panels
- `v-horizontal`: compact row lists and sidebars

## Homepage/index-specific behavior

The original `index.html` looks especially polished because it adds a gallery layer on top of the base Birchline language:

- larger `.wrap.home` canvas, max-width `1120px`
- big `header.masthead` with bottom rule
- two-column `.hero-grid`
- decorative `.hero-fig` showing markdown vs HTML panes
- pill-style `.toc`
- `.demo-grid` offset by `50px` from numbered section headers
- rich `.demo-card` link cards with SVG thumbnails, hover lift, and thumbnail color transitions

These are not required for every page. Treat them as the **catalog/index template**, not the base application style.

## Local fixture generation

Run `python3 scripts/generate-birchline-examples.py` from the repo root to regenerate the standalone example pages. The generator embeds `birchline-core.css` and `birchline-components.css` directly into each artifact and intentionally excludes `birchline-homepage.css`.

Current fixtures:

- `birchline/examples/smoke-test.html`: broad primitive coverage.
- `birchline/examples/chat-summary.html`: extracted conversation summary with a responsive matrix.
- `birchline/examples/implementation-plan.html`: planning artifact with steps, stats, and risk cards.
- `birchline/examples/incident-report.html`: operational report with impact stats, timeline, and corrective-action matrix.
- `birchline/examples/research-brief.html`: explanatory brief with callout, horizontal rows, and evidence bars.
