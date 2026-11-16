import { useMutation } from "@tanstack/react-query";
import { toBlob } from "html-to-image";
import { CHART_DPI } from "@/constants/api.constants";
import { MUTATION_KEYS } from "@/constants/query.constants";
import {
  EXPORTS,
  type ExportKind,
  SUMMARY_CAPTURE,
} from "@/constants/results.constants";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import { getChart } from "@/services/charts.service";
import { exportXlsx } from "@/services/export.service";
import { saveBlob } from "@/utils/download.utils";

/** The file of a server-rendered export (XLSX or a chart at download resolution). */
function exportFile(
  snapshot: AnalysisRequest,
  kind: ExportKind,
): Promise<Blob> {
  switch (kind) {
    case "xlsx":
      return exportXlsx(snapshot);
    case "causal":
      return getChart(
        snapshot,
        "causal-diagram",
        "standard",
        CHART_DPI.DOWNLOAD,
      );
    case "heatmapStandard":
      return getChart(snapshot, "heatmap", "standard", CHART_DPI.DOWNLOAD);
    case "heatmapCluster":
      return getChart(snapshot, "heatmap", "cluster", CHART_DPI.DOWNLOAD);
    case "summary":
      throw new Error("The summary is captured in the browser");
  }
}

/** PNG of a rendered element (the summary panel), embedding its fonts. */
export async function captureElement(node: HTMLElement): Promise<Blob> {
  const blob = await toBlob(node, {
    pixelRatio: SUMMARY_CAPTURE.PIXEL_RATIO,
    backgroundColor: SUMMARY_CAPTURE.BACKGROUND,
  });
  if (!blob) throw new Error("The summary could not be captured.");
  return blob;
}

/** Download an export of the results snapshot under Qt's file name. */
export function useExportFile(snapshot: AnalysisRequest) {
  return useMutation({
    mutationKey: MUTATION_KEYS.EXPORT_FILE,
    mutationFn: async (kind: ExportKind) => {
      saveBlob(await exportFile(snapshot, kind), EXPORTS[kind].filename);
    },
  });
}

/** Capture the summary panel and download it as `summary.png`. */
export function useSummaryExport() {
  return useMutation({
    mutationKey: MUTATION_KEYS.EXPORT_FILE,
    mutationFn: async (node: HTMLElement) => {
      saveBlob(await captureElement(node), EXPORTS.summary.filename);
    },
  });
}
