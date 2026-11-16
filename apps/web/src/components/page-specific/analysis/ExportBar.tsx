import { useRef, useState } from "react";
import { DownloadButton } from "@/components/general/DownloadButton";
import { InlineError } from "@/components/general/InlineError";
import { SummaryPanel } from "@/components/page-specific/analysis/SummaryPanel";
import {
  EXPORTS,
  type ExportKind,
  SUMMARY_CAPTURE,
} from "@/constants/results.constants";
import { useExportFile, useSummaryExport } from "@/hooks/export.hook";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import type { AnalysisData } from "@/interfaces/result.interface";
import { errorMessage } from "@/utils/api.utils";

const SERVER_EXPORTS: readonly ExportKind[] = [
  "causal",
  "heatmapStandard",
  "heatmapCluster",
];

/**
 * Qt's export buttons. XLSX and charts (300 dpi) come from the API; the summary PNG is captured in
 * the browser from an off-screen copy of the summary panel, so it works from any tab.
 */
export function ExportBar({
  snapshot,
  data,
}: {
  snapshot: AnalysisRequest;
  data: AnalysisData;
}) {
  const exportFile = useExportFile(snapshot);
  const summary = useSummaryExport();
  const [capturing, setCapturing] = useState(false);
  const started = useRef(false);
  const error = exportFile.error ?? summary.error;

  const startCapture = () => {
    exportFile.reset();
    started.current = false;
    setCapturing(true);
  };
  const capture = (node: HTMLDivElement | null) => {
    if (!node || started.current) return;
    started.current = true;
    summary.mutate(node, { onSettled: () => setCapturing(false) });
  };
  const download = (kind: ExportKind) => {
    summary.reset();
    exportFile.mutate(kind);
  };
  const isPending = (kind: ExportKind) =>
    exportFile.isPending && exportFile.variables === kind;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-2">
        <DownloadButton
          label={EXPORTS.xlsx.label}
          pending={isPending("xlsx")}
          onClick={() => download("xlsx")}
        />
        <DownloadButton
          label={EXPORTS.summary.label}
          pending={capturing}
          onClick={startCapture}
        />
        {SERVER_EXPORTS.map((kind) => (
          <DownloadButton
            key={kind}
            label={EXPORTS[kind].label}
            pending={isPending(kind)}
            onClick={() => download(kind)}
          />
        ))}
      </div>
      <InlineError message={error ? errorMessage(error) : null} />
      {capturing && (
        <div
          aria-hidden="true"
          inert
          className="pointer-events-none fixed top-0 -left-[20000px]"
          style={{ width: SUMMARY_CAPTURE.WIDTH_PX }}
        >
          <SummaryPanel data={data} ref={capture} />
        </div>
      )}
    </div>
  );
}
