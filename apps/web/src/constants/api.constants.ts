export const API_V1_PREFIX = "/api/v1";

export const API_ENDPOINTS = {
  HEALTH: "/health",
  SCALES: "/scales",
  WEIGHTS_DEFAULTS: "/weights/defaults",
  WEIGHTS_NORMALIZE: "/weights/normalize",
  ANALYSIS: "/analysis",
  EXPORT_XLSX: "/analysis/export/xlsx",
  CHART_CAUSAL_DIAGRAM: "/analysis/charts/causal-diagram",
  CHART_HEATMAP: "/analysis/charts/heatmap",
  IMPORT_MATRIX: "/imports/matrix",
  IMPORT_WORKBOOK: "/imports/workbook",
  EXPLANATIONS: "/explanations",
  EXPLANATION_PROVIDERS: "/explanations/providers",
} as const;

/** Chart resolutions the API accepts: on screen and for downloads. */
export const CHART_DPI = { DISPLAY: 100, DOWNLOAD: 300 } as const;
