import { queryOptions, useQuery } from "@tanstack/react-query";
import { CHART_DPI } from "@/constants/api.constants";
import { QUERY_KEYS } from "@/constants/query.constants";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import type { ChartKind, HeatmapMode } from "@/interfaces/result.interface";
import { getChart } from "@/services/charts.service";

/** Query of one chart for the results snapshot (keyed by its hash, not the request). */
export function chartQueryOptions(
  snapshot: AnalysisRequest,
  snapshotHash: string,
  kind: ChartKind,
  mode: HeatmapMode,
  dpi: number = CHART_DPI.DISPLAY,
) {
  return queryOptions({
    queryKey: [QUERY_KEYS.CHART, snapshotHash, kind, mode, dpi],
    queryFn: () => getChart(snapshot, kind, mode, dpi),
    staleTime: Number.POSITIVE_INFINITY,
    retry: false,
  });
}

/** A chart PNG of the results, as shown on screen. */
export function useChart(
  snapshot: AnalysisRequest,
  snapshotHash: string,
  kind: ChartKind,
  mode: HeatmapMode = "standard",
) {
  return useQuery(chartQueryOptions(snapshot, snapshotHash, kind, mode));
}
