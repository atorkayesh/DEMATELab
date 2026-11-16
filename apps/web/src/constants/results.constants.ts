import type { MatrixKind } from "@/interfaces/result.interface";

export const RESULTS_TEXT = {
  TITLE: "Results",
  SUBTITLE:
    "Analysis complete. Review the cause-and-effect relationships below.",
  OUTDATED: "Your inputs changed since this analysis. Run again to update.",
  RERUN: "Re-run",
  NOT_AVAILABLE: "Total relation matrix is not available.",
  LOADING_CHART: "Rendering chart…",
  ZOOM_IN: "Zoom In",
  ZOOM_OUT: "Zoom Out",
  CLUSTER_CHECKBOX: "Show cluster-based heatmap",
  EMPTY_GROUP: "—",
} as const;

/** Zoom factor per click, as in Qt. */
export const ZOOM_STEP = 1.2;

/** Export buttons and their files (Qt's labels and default file names). */
export const EXPORTS = {
  xlsx: { label: "Export Results to XLSX", filename: "dematel_results.xlsx" },
  summary: { label: "Export Summary to PNG", filename: "summary.png" },
  causal: {
    label: "Export Causal Diagram to PNG",
    filename: "causal_diagram.png",
  },
  heatmapStandard: {
    label: "Export Standard Heatmap to PNG",
    filename: "heatmap_standard.png",
  },
  heatmapCluster: {
    label: "Export Cluster Heatmap to PNG",
    filename: "heatmap_cluster.png",
  },
} as const;

export type ExportKind = keyof typeof EXPORTS;

/** Options of the client-side summary capture (`html-to-image`). */
export const SUMMARY_CAPTURE = {
  PIXEL_RATIO: 2,
  BACKGROUND: "#fffdf9",
  WIDTH_PX: 1100,
} as const;

export const TAB_IDS = {
  SUMMARY: "summary",
  SCORES: "scores",
  CAUSAL: "causal",
  HEATMAP: "heatmap",
  AI: "ai",
} as const;

export const TAB_LABELS = {
  SUMMARY: "Summary",
  SCORES: "R/C Scores",
  CAUSAL: "Causal Diagram",
  HEATMAP: "Heatmap",
  AI: "AI Explanation",
} as const;

/** Matrix tabs in order: crisp names, prefixed for fuzzy/grey/Z results. */
export const MATRIX_TABS: readonly { kind: MatrixKind; title: string }[] = [
  { kind: "direct", title: "Direct Matrix" },
  { kind: "normalized", title: "Normalized Matrix" },
  { kind: "total", title: "Total Relation Matrix" },
];

/** On-screen prefix of the matrix tabs per solver (Z reads "Fuzzy Z", Settled Decision 7). */
export const MATRIX_TAB_PREFIX: Record<string, string> = {
  dematel: "",
  fuzzy_dematel: "Fuzzy ",
  grey_dematel: "Grey ",
  fuzzy_z_dematel: "Fuzzy Z ",
};

export const SCORE_HEADERS = {
  CRISP: ["Factor", "R", "C", "R+C", "R-C"],
  TUPLE: ["Factor", "R", "C", "Prominence", "Relation"],
} as const;

export const SUMMARY_TEXT = {
  INSIGHTS_TITLE: "Summary Insights",
  INSIGHTS_SUBTITLE:
    "Key signals from the DEMATEL analysis, highlighting the most important relationships for quick insight.",
  CONFIG_TITLE: "Analysis Configuration",
  RESULT_TYPE: "Result Type",
  THRESHOLD_METHOD: "Threshold Method",
  THRESHOLD_VALUE: "Threshold Value",
  CAUSE_TITLE: "Cause Group (Driving Factors)",
  EFFECT_TITLE: "Effect Group (Dependent Factors)",
  RANKING_TITLE: "Prominence and Relation Analysis",
} as const;

/** Qt's stat boxes: title and fixed description. */
export const STAT_BOXES = {
  DRIVING: {
    title: "Driving Factors",
    description: "Majority of factors act as system drivers.",
  },
  DEPENDENT: {
    title: "Dependent Factors",
    description: "Primarily influenced factor in the system.",
  },
  PROMINENCE: {
    title: "Top Prominence",
    description: "Highest overall importance among factors.",
  },
  RELATION: {
    title: "Strongest Relation",
    description: "Strongest net driving influence detected.",
  },
} as const;
