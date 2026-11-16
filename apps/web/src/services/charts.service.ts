import { API_ENDPOINTS } from "@/constants/api.constants";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import type { ChartKind, HeatmapMode } from "@/interfaces/result.interface";
import { apiBlob, jsonPost } from "@/utils/api.utils";

/** Path and query of a chart: the causal diagram, or the heatmap in `mode`. */
export function chartPath(
  kind: ChartKind,
  mode: HeatmapMode,
  dpi: number,
): string {
  if (kind === "causal-diagram") {
    return `${API_ENDPOINTS.CHART_CAUSAL_DIAGRAM}?dpi=${dpi}`;
  }
  return `${API_ENDPOINTS.CHART_HEATMAP}?mode=${mode}&dpi=${dpi}`;
}

/** A chart as a PNG; a cluster heatmap that cannot be computed rejects with the API's message. */
export function getChart(
  request: AnalysisRequest,
  kind: ChartKind,
  mode: HeatmapMode,
  dpi: number,
): Promise<Blob> {
  return apiBlob(chartPath(kind, mode, dpi), jsonPost(request));
}
