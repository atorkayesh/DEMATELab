import { ChartImage } from "@/components/page-specific/analysis/ChartImage";
import { RESULTS_TEXT, TAB_LABELS } from "@/constants/results.constants";
import { useChart } from "@/hooks/chart.hook";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";

/** The causal diagram rendered by the API. */
export function CausalDiagramPanel({
  snapshot,
  snapshotHash,
  available,
}: {
  snapshot: AnalysisRequest;
  snapshotHash: string;
  available: boolean;
}) {
  if (!available) {
    return (
      <p className="text-muted-foreground">{RESULTS_TEXT.NOT_AVAILABLE}</p>
    );
  }
  return <CausalDiagramImage snapshot={snapshot} snapshotHash={snapshotHash} />;
}

function CausalDiagramImage({
  snapshot,
  snapshotHash,
}: {
  snapshot: AnalysisRequest;
  snapshotHash: string;
}) {
  const chart = useChart(snapshot, snapshotHash, "causal-diagram");
  return (
    <ChartImage
      blob={chart.data}
      isPending={chart.isPending}
      error={chart.error}
      alt={TAB_LABELS.CAUSAL}
    />
  );
}
