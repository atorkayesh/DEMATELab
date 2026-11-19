# Which Browser Chart Library Could Replace The Server-Rendered Matplotlib Charts?

**Date:** 18 November, 2026
**Author:** Claude Code (planning agent) for Youpele Michael
**Status:** Complete
**Scope:** Browser chart libraries for the DEMATELab and Policy Coherence Kit (PCK) web apps (TanStack Start,
React 19, shadcn on Base UI, Tailwind v4): shadcn/ui charts, Recharts, Apache ECharts, visx, Nivo, Plotly.js,
Observable Plot, and the graph libraries Cytoscape.js, Sigma.js with graphology, React Flow (xyflow), vis-network
and D3-force. Also where the maths should live (API vs browser) and how exports stay consistent. Out of scope:
commercial libraries (Highcharts, amCharts, AG Charts Enterprise), 3D/WebGPU charts, and any prototype. No
library was installed or run; every capability below comes from documentation, the npm registry or source code.
The same core text is in both repositories; only "Relevance" differs.

## Summary

**Apache ECharts 6 is the only evaluated library that covers every chart the two apps need with one
dependency**: heatmaps (including a categorical cluster heatmap), a directed weighted graph with arrows, edge
widths, curved two-way edges and edge labels on fixed coordinates or on a Cartesian axis, labelled scatter plots
with shaded quadrants and reference lines, and bar/range charts. It exports PNG at any pixel ratio and SVG,
has an `aria` layer with decal patterns, runs server-side to SVG without a DOM, is Apache-2.0 and actively
released (6.1.0, 19 May 2026). Its costs are bundle size (359 KB gzip for the whole package; tree-shaking via
`echarts/core` is documented but the real size for our chart set was not measured) and theming: it draws on
canvas or its own SVG, so shadcn CSS variables must be read with `getComputedStyle` and passed in as a theme.

**shadcn/ui charts are a thin layer over Recharts v3** (the Base UI variant exists and uses the same Recharts
code). They give the best shadcn look and accessibility for bar, line, area and scatter charts, but Recharts has
no heatmap and no graph/arrow series, so the causal diagram, the PCK network and the heatmaps would still need a
second library. Graph-specific libraries (Cytoscape.js first) are only worth adding if interactive graph
exploration beyond ECharts' roam/drag/highlight is wanted later.

**Keep all maths in the API**: the API returns chart data (node positions, filtered edges with weights and
widths, thresholds, cluster codes, layout coordinates, PCA coordinates); the browser only maps data to visuals.
Neither app's XLSX export contains charts today, so the export consistency question is only about the PNG/SVG
downloads, which the browser can produce from the same chart options it shows.

Confidence: high for licences, versions and the presence of the documented features; medium for fitness in
practice (bundle size after tree-shaking, PNG fidelity at 300 dpi equivalent, look next to shadcn components),
which needs a short spike.

## Question

Can the server-rendered matplotlib PNG charts (DEMATELab today; PCK's first port) be replaced with charts drawn
in the browser, using shadcn charts or a better JavaScript library, without losing numerical parity, export
quality (300 dpi PNG) or SSR compatibility with TanStack Start? Interactive, themeable, accessible charts would
replace zoomable images, but the existing decisions chose server rendering to avoid a second implementation of
the plots ([DEMATELab decision](../decisions/2026-11-16-stateless-api-with-server-rendered-charts.md) in the
DEMATELab repository).

### Needs (both apps)

| Need | DEMATELab | PCK |
|---|---|---|
| Heatmap | Total relation matrix, continuous colour scale with colourbar | None in the legacy app (the aggregated matrix is a coloured grid table; a "Conflict and Consensus Heatmap" exists only as dead code) |
| Clustered heatmap | 4-group KMeans cluster codes with a categorical legend; **no dendrogram** today | None |
| Directed weighted graph | Causal diagram: nodes at (prominence, relation) on Cartesian axes, edges above the threshold with arrows, width scaled by weight, curved mutual edges | Network: signed edges (green/red), width by abs(score) bands, arrows, two-way pairs, four layouts (circular, force-directed, spectral, shell), ego view with edge labels |
| Scatter with labels and quadrants | Causal diagram axes: dashed zero line and dotted mean-prominence line (cause/effect quadrants) | PCA scatter: code labels in nodes, axes at zero, colour by entropy category, hover with the full name (no loadings, so not a true biplot) |
| Bar/range | Prominence ranking (HTML bars today) | Range of influence and coherence scores are tables today; bars would be new |
| Export | PNG at 300 dpi (8 x 6 in, about 2400 x 1800 px) | PNG (legacy screen grabs, a known defect) |

## Sources And Method

- npm registry metadata (`registry.npmjs.org/<package>`) for latest version, publish date and licence, queried
  18 November, 2026.
- GitHub repository metadata (`api.github.com/repos/...`, `pushed_at`, stars, licence), queried 18 November, 2026.
- Bundle sizes from bundlephobia's API (`bundlephobia.com/api/size`), queried 18 November, 2026. These are
  whole-package minified/gzip sizes, **not** tree-shaken sizes.
- Official documentation pages and source files listed under References, all accessed 18 November, 2026.
- Repository facts from both repositories (file paths cited in the Relevance section).
- Search terms: "shadcn chart recharts v3 base ui", "echarts server side rendering svg", "echarts graph
  edgeSymbol autoCurveness", "cytoscape png export scale", "react flow download image", "plotly toImage scale",
  "observable plot document option", "TanStack ClientOnly".
- Not done: no prototype, no measured tree-shaken bundle, no visual comparison with matplotlib.

## Findings

### 1. shadcn/ui charts (Recharts v3)

- The shadcn `chart` component "now uses Recharts v3" and states "We use Recharts under the hood"; it adds
  `ChartContainer`, `ChartTooltip`/`ChartTooltipContent`, `ChartLegend`/`ChartLegendContent` and a `ChartConfig`
  type for labels and colours (shadcn chart docs, Base UI variant page `docs/components/base/chart`).
- Colours come from CSS variables: `--chart-1` … `--chart-5` in `:root`/`.dark`, referenced as `var(--chart-1)`
  (not `hsl(var(...))` with Recharts v3) (shadcn chart docs).
- The Base UI page exists next to the Radix and React Aria variants; the page does not describe any difference,
  and the component wraps Recharts rather than a primitive library (inference: the Base UI variant is
  functionally the same chart). Install: `pnpm dlx shadcn@latest add chart`. `shadcn` CLI latest is 4.23.0
  (27 October, 2026).
- Documented chart types are Recharts' (area, bar, line, pie, radar, radial; scatter via Recharts). No heatmap,
  graph or arrow components are documented (shadcn chart docs; Recharts API).

### 2. Recharts

- Latest 3.11.0, 17 November, 2026, MIT; peer `react ^16.8 … ^19` (npm). v3.11.0 adds a context theming
  system, patterns for accessibility, label halos/backgrounds, and a React 19 Suspense fix (GitHub releases).
- `accessibilityLayer` (keyboard access and screen-reader support) is **on by default since 3.0** (3.0
  migration guide).
- SVG output via React components, so it renders on the server when width and height are fixed; responsive
  containers measure the DOM and render after mount (inference from the component model; not tested).
- No heatmap, no directed graph, no arrowheads on scatter connections. A heatmap can be faked with custom
  shapes in a scatter chart, and quadrants with `ReferenceArea`/`ReferenceLine` (inference from the API; the
  heatmap workaround is not a supported chart type).
- Whole-package size 173 KB gzip (bundlephobia). Image export is not built in (needs SVG serialisation or
  `html-to-image`, which DEMATELab already uses for its summary PNG).

### 3. Apache ECharts

- Latest 6.1.0, 19 May, 2026, Apache-2.0; 6.0.0 (30 July; the release page omits the year, 2025 by its order) added a new default
  theme with dynamic theme registration and switching, a matrix coordinate system, a chord series, axis breaks,
  scatter jittering and graph thumbnails (GitHub releases). `echarts-for-react` 3.1.0 (17 November, 2026, MIT)
  is an optional React wrapper.
- **Graph series:** `layout: 'none'` uses node `x`/`y` given by the caller; `'circular'` and `'force'` are built
  in. The series can be placed on a `cartesian2d` coordinate system, so nodes can sit on value axes (prominence,
  relation). `edgeSymbol: ['none','arrow']`, per-edge `lineStyle.width`/`color`/`curveness`, `edgeLabel`, and
  `autoCurveness` for several edges between the same two nodes are documented options (ECharts option reference,
  `series-graph`).
- **Heatmap series** on category axes with `visualMap` (continuous or piecewise/categorical) is the standard
  ECharts heatmap (ECharts option reference). A dendrogram is not built in; it can be drawn with a `custom`
  series or `lines` on extra grids from coordinates the API computes (inference).
- **Scatter** with `label`, `markLine` (reference lines) and `markArea` (shaded quadrants) covers the causal
  diagram axes and a PCA plot (ECharts option reference).
- **Export:** `getDataURL({type, pixelRatio, backgroundColor, excludeComponents})` gives PNG/JPEG from the
  canvas renderer and SVG from the SVG renderer; `renderToSVGString()` (since 5.3.0) renders SVG with
  `ssr: true` and no DOM, so the same option object can be rendered in Node (ECharts instance API; SSR handbook).
  A 300 dpi equivalent of the 8 x 6 in matplotlib figure is an 800 x 600 chart exported with `pixelRatio: 3`
  (2400 x 1800 px). Canvas PNGs carry no dpi metadata (`pHYs`) unless added (inference; matplotlib writes it).
- **SSR:** server-side SVG strings (5.3.0+) and an under-4 KB client runtime for hydrating them (5.5.0+, no
  mouse-move tooltips) (SSR handbook). For the apps, client-only rendering behind TanStack Router's `ClientOnly`
  with a fallback is simpler (TanStack docs).
- **Accessibility:** `aria.show` generates a text description from title, series and data; `aria.decal` adds
  patterns as a second cue besides colour; both are off by default and need the Aria component imported (ECharts
  accessibility handbook). There is no keyboard navigation of data points comparable to Recharts' layer
  (inference from the handbook, which describes none).
- **Theming:** themes are JavaScript objects; CSS variables are not mentioned in the release notes, so values
  must be read from the document and passed to the theme (inference).
- Whole-package size 359 KB gzip (bundlephobia); the documented `echarts/core` import path registers only the
  charts, components and renderer used (tree-shaken size not measured).

### 4. visx (Airbnb)

- 4.0.0, 11 June, 2026, MIT, React 18/19 peers (npm). Low-level SVG primitives (`@visx/heatmap` is 1 KB gzip,
  `@visx/hierarchy` for trees/dendrograms, `@visx/network`, `@visx/xychart`). Everything (axes, legends,
  arrows via SVG markers, tooltips, export) is assembled by hand. Repository last pushed 22 June, 2026.
- Best fit when full control and pure SVG matter more than development time; renders on the server like any
  React SVG (inference).

### 5. Nivo

- 0.99.0, last published 23 May, 2025, MIT (npm); repository last pushed 21 July, 2026 (GitHub). Has
  `@nivo/heatmap`, `@nivo/scatterplot` and `@nivo/network` (force layout; the network types expose link
  thickness, no arrow option was found in `packages/network/src/types.ts`), and `@nivo/static` for server-side
  rendering. No release for about 18 months is a maintenance risk.

### 6. Plotly.js

- 4.3.0, 10 November, 2026, MIT (npm; changelog shows 4.0.0 on 24 August, 2026). Heatmaps, scatter with
  annotations (arrows), shapes for quadrants; `Plotly.toImage` exports png, jpeg, webp, svg; the source coerces
  a `scale` option for higher resolution (`src/plot_api/to_image.js`). No graph layout; networks are drawn as
  scatter lines plus annotation arrows.
- `plotly.js-dist-min` is 1,376 KB gzip (bundlephobia), roughly four times ECharts' whole package. Styling is
  Plotly's own, hard to match shadcn.

### 7. Observable Plot

- 0.6.19, 5 November, 2026, ISC (npm). Returns SVG elements; the `document` option allows server-side rendering
  with a virtual DOM in Node (Plot docs, `features/plots.md`). Marks include `cell` (heatmap), `tree`
  (dendrogram), `link` and `arrow`, where `bend` draws curved directed edges (Plot docs, `marks/arrow.md`).
- Not a React library (mount the returned SVG via a ref); interaction is limited to tips; whole package 124 KB
  gzip. A good static, SVG-first option; pre-1.0 versioning.

### 8. Graph-specific libraries

| Library | Facts (sources: npm, docs, repo) |
|---|---|
| Cytoscape.js 3.35.0 (10 Nov 2026, MIT) | Canvas renderer; edges with `target-arrow-shape`, `curve-style` (bezier handles parallel edges), labels; layouts `preset`, `circle`, `cose`, `breadthfirst`, more as extensions; `cy.png({scale, full, bg, output:'blob'})` and `cy.jpg`; runs headless in Node for analysis (not image export). SVG export needs `cytoscape-svg`, which is **GPL-3.0** (npm). 136 KB gzip. `react-cytoscapejs` was last released 2 September, 2022. |
| Sigma.js 4.0.6 (10 Nov 2026, MIT) + graphology 0.26.0 | WebGL renderer for large graphs; core has arrow extremities and curved edge paths (`packages/sigma/src/rendering/edges/...`), `renderEdgeLabels` setting; `@sigma/export-image` 4.0.0; `@react-sigma/core` 6.0.0. 95 KB + 13 KB gzip. Built for thousands of nodes; our graphs have at most about 100 nodes. |
| React Flow / `@xyflow/react` 13.0.2 (17 Nov 2026, MIT) | Nodes are React DOM elements, edges SVG; aimed at node editors and diagrams, not data-driven weighted graphs. The image-export example uses `html-to-image` pinned to 1.11.11 because later versions "do not export images properly" (React Flow example). 86 KB gzip. |
| vis-network 10.1.5 (8 Nov 2026, Apache-2.0 OR MIT) | Canvas, physics layouts, arrows, smooth curves, edge labels; imperative API, no React wrapper in the package. 116 KB gzip. |
| D3-force 3.0.1 (3 Nov 2026, ISC) | Layout simulation only (6 KB gzip); drawing, arrows and export are separate work. |

### 9. Where the maths lives, and export consistency

- Both apps already state that the browser does no domain maths: DEMATELab's web rules say "No DEMATEL maths
  in the browser" (`apps/web/AGENTS.md`), and every number has a parity requirement against the legacy app
  (plan authoring guides). Chart geometry that encodes a rule (edges strictly above the threshold, line-width
  scaling, mutual-edge curvature, cluster ranking; PCK's layouts, betweenness-based shells, PCA) therefore
  belongs in the API, where it is already tested.
- Options for the API contract:
  1. **Semantic chart data** (nodes, edges, weights, widths, curvature, thresholds, codes, coordinates): the
     browser maps it to any library. Library-independent, testable with pytest, and the same payload can feed
     a later server-side export. Recommended.
  2. **Library-specific option JSON** (the API emits an ECharts option): one rendering path for screen and
     export, but couples the API to a JavaScript library and moves UI text and colours into Python.
  3. **Browser computes geometry or layouts** (for example ECharts' own force layout): least API work, but
     breaks the "no maths in the browser" rule and makes downloads non-reproducible (force layouts depend on
     the run).
- **XLSX has no charts in either app.** DEMATELab's export writes matrices, `R_C_Scores` and `Summary` with
  pandas (`apps/api/features/xlsx_export_feature.py:1-8`); PCK's legacy export writes per-DM and per-run sheets
  and omits PCA and insights (PCK logic inventory, section 6). openpyxl can create native Excel charts (area,
  bar, bubble, line, scatter, pie, radar, stock, surface) but no heatmap or network (openpyxl 3.1.3 docs), and
  embedding a picture means rendering a PNG on the server. Consistency therefore means: (a) the numbers in the
  XLSX and the chart data come from the same API computation; (b) PNG/SVG downloads are produced from the
  same option object the screen shows.

## Comparison

Scores: **Yes** built in and documented; **Partial** possible with custom work; **No** not supported.
Sizes are whole-package gzip from bundlephobia (not tree-shaken).

| Criterion | shadcn chart (Recharts 3) | ECharts 6 | visx 4 | Nivo 0.99 | Plotly.js 4 | Observable Plot | Cytoscape.js | Sigma.js |
|---|---|---|---|---|---|---|---|---|
| Heatmap (continuous + categorical legend) | No (workaround) | Yes | Partial (primitives) | Yes | Yes | Yes (`cell`) | No | No |
| Heatmap with dendrogram | No | Partial (custom series) | Partial (`hierarchy`) | No | Partial (shapes) | Partial (`tree` + `cell`) | No | No |
| Directed weighted graph, arrows, widths, curved two-way edges | No | Yes (`graph`, `edgeSymbol`, `curveness`, `autoCurveness`) | Partial (SVG markers) | Partial (no arrows found) | Partial (annotations) | Yes (`arrow` with `bend`, static) | Yes | Yes |
| Graph on fixed coordinates / Cartesian axes | No | Yes (`layout:'none'`, `cartesian2d`) | Yes | No | Yes | Yes | Yes (`preset`, no axes) | Yes (no axes) |
| Scatter with labels, reference lines, quadrants | Yes | Yes | Yes | Yes | Yes | Yes | No | No |
| Bar / range | Yes | Yes | Yes | Yes | Yes | Yes | No | No |
| PNG at 300 dpi equivalent | Partial (`html-to-image`) | Yes (`pixelRatio`) | Partial (serialise SVG) | Partial | Yes (`scale`) | Partial (serialise SVG) | Yes (`scale`) | Yes (`@sigma/export-image`) |
| SVG export | Partial (DOM SVG) | Yes (SVG renderer) | Yes (DOM SVG) | Yes (SVG charts) | Yes | Yes | Partial (GPL plugin) | No (WebGL) |
| SSR with TanStack Start | Yes with fixed size | Client-only or SVG string SSR | Yes | Yes (`@nivo/static`) | Client-only | Yes (`document` option) | Client-only | Client-only |
| Accessibility | Best (`accessibilityLayer` default on) | `aria` description + decals | Manual | Partial | Partial | Manual | Manual | Manual |
| Theming with shadcn CSS variables | Native (`var(--chart-n)`) | Read vars into a theme | Native (SVG) | Theme object | Layout object | Native (SVG styles) | Stylesheet object | Settings object |
| Licence | MIT | Apache-2.0 | MIT | MIT | MIT | ISC | MIT (SVG plugin GPL-3.0) | MIT |
| Maintenance (latest release) | 17 Nov 2026 | 19 May 2026 (repo active Oct 2026) | 11 Jun 2026 | 23 May 2025 | 10 Nov 2026 | 5 Nov 2026 | 10 Nov 2026 | 10 Nov 2026 |
| Size (gzip, whole package) | 173 KB | 359 KB | 1 KB per primitive | 48 KB (heatmap) | 1,376 KB | 124 KB | 136 KB | 95 KB + 13 KB |
| Covers every need alone | No | **Yes** | Yes, with much custom code | No | Mostly, heavy | Mostly, static only | No | No |

## Relevance To DEMATELab

- **Charts in scope:** the causal diagram (`apps/api/features/causal_diagram_chart_feature.py`,
  `apps/api/utils/influence_map_utils.py`) and the standard/cluster heatmaps
  (`apps/api/features/heatmap_chart_feature.py`), shown as zoomable PNGs (`apps/web/src/components/
  page-specific/analysis/{CausalDiagramPanel,HeatmapPanel,ChartImage}.tsx`) and downloaded at 300 dpi
  (`ExportBar.tsx`, filenames `causal_diagram.png`, `heatmap_standard.png`, `heatmap_cluster.png`).
- **ECharts mapping:** the causal diagram is a `graph` series on `cartesian2d` with nodes at (prominence,
  relation), green/red by `relation > 0`, `markLine` for the zero and mean-prominence lines, arrows via
  `edgeSymbol`, widths and curvature from the API (one-way `rad` 0.06, mutual pairs ±0.20, from
  `InfluenceMapGeometry.draw_edges`). The heatmaps are `heatmap` series with a continuous `visualMap` (standard)
  or a piecewise `visualMap` over the cluster codes (cluster). No dendrogram is needed today.
- **Already returned by the API:** `prominence`, `relation`, `crisp_total_matrix` and `threshold_value`
  (`apps/api/models/analysis_result_models.py:19-32`). **Still API-side maths:** the mean-matrix fallback when
  the threshold is missing, edge filtering (strictly above the threshold, no self-loops), line-width scaling,
  mutual-edge pairing and KMeans cluster codes. These need a chart-data response so the browser stays maths-free.
- **What changes in the decisions:** the stateless-API decision chose server rendering to keep the Qt look and
  avoid a second implementation; browser charts will not be pixel-identical to the Qt/matplotlib charts, so a
  superseding decision is needed. Matplotlib, the Inter font registration (`apps/api/main.py:24-26`),
  `MPLCONFIGDIR` and the `fonts-dejavu-core` layer (`apps/api/Dockerfile.{dev,prod}`) can go once no PNG endpoint
  remains.
- **shadcn theme:** `--chart-1…5` are greyscale neutrals in `apps/web/src/styles.css` (as listed in PCK's
  conventions inventory report); cause/effect green/red and a heatmap ramp need new tokens either way.
- **Unknown:** tree-shaken ECharts size for `graph` + `heatmap` + `scatter` + `bar` with the SVG and canvas
  renderers; how a 100-factor heatmap and a dense causal diagram read at 320 px width.

## Open Questions

- Tree-shaken bundle size and first-render time of ECharts for the needed chart set; answer with a spike build
  (`vite build` and the bundle report).
- Whether PNG downloads must carry 300 dpi metadata (`pHYs`) or only 2400 x 1800 px; answer with the users who
  put the figures into papers.
- Whether interactive graph features (dragging nodes, filtering edges by weight, ego view) are wanted beyond
  roam/zoom/highlight; if yes, re-check Cytoscape.js for the network only.
- Whether a server-side export path (ECharts `renderToSVGString` in the web server, rasterised to PNG) is
  needed for downloads outside the browser; nothing requires it today.

## References

- shadcn/ui, "Chart" (Base UI variant), https://ui.shadcn.com/docs/components/base/chart and
  https://ui.shadcn.com/docs/components/chart, accessed 18 November, 2026.
- Recharts, GitHub releases (v3.11.0, 17 November, 2026), https://github.com/recharts/recharts/releases; "3.0
  migration guide", https://github.com/recharts/recharts/wiki/3.0-migration-guide, accessed 18 November, 2026.
- Apache ECharts, GitHub releases (6.1.0, 19 May, 2026), https://github.com/apache/echarts/releases; option
  reference `series-graph`, https://echarts.apache.org/en/llms-documents/option-parts/option.series-graph.md;
  instance API, https://echarts.apache.org/en/llms-documents/api-parts/api.echartsInstance.md; "Server Side
  Rendering", https://echarts.apache.org/handbook/en/how-to/cross-platform/server/; "Accessibility",
  https://echarts.apache.org/handbook/en/best-practices/aria/; all accessed 18 November, 2026.
- Observable Plot docs, `docs/features/plots.md` and `docs/marks/arrow.md`,
  https://github.com/observablehq/plot/tree/main/docs, accessed 18 November, 2026.
- Plotly, "Static image export in JavaScript", https://plotly.com/javascript/static-image-export/; source
  `src/plot_api/to_image.js` and `CHANGELOG.md`, https://github.com/plotly/plotly.js, accessed 18 November, 2026.
- Cytoscape.js documentation, https://js.cytoscape.org/, accessed 18 November, 2026.
- Sigma.js, https://www.sigmajs.org/ and repository tree https://github.com/jacomyal/sigma.js, accessed
  18 November, 2026.
- React Flow, "Download Image" example, https://reactflow.dev/examples/misc/download-image, accessed
  18 November, 2026.
- Nivo network types, https://github.com/plouc/nivo/blob/master/packages/network/src/types.ts, accessed
  18 November, 2026.
- TanStack Router, "ClientOnly component",
  https://tanstack.com/router/latest/docs/framework/react/api/router/clientOnlyComponent, accessed
  18 November, 2026.
- openpyxl 3.1.3, "Charts", https://openpyxl.readthedocs.io/en/stable/charts/introduction.html, accessed
  18 November, 2026.
- npm registry, https://registry.npmjs.org/ (versions, dates, licences), and bundlephobia,
  https://bundlephobia.com/ (sizes), both queried 18 November, 2026.
