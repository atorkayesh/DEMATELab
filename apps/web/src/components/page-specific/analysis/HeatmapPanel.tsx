import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { InlineError } from "@/components/general/InlineError";
import { ChartImage } from "@/components/page-specific/analysis/ChartImage";
import { Checkbox } from "@/components/ui/checkbox";
import { RESULTS_TEXT, TAB_LABELS } from "@/constants/results.constants";
import { chartQueryOptions, useChart } from "@/hooks/chart.hook";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import type { HeatmapMode } from "@/interfaces/result.interface";
import { errorMessage } from "@/utils/api.utils";

/**
 * The heatmap with Qt's "Show cluster-based heatmap" checkbox. When clustering fails the API's
 * message ("Could not generate cluster heatmap: …") is shown and the box is unticked again.
 */
export function HeatmapPanel({
  snapshot,
  snapshotHash,
  available,
}: {
  snapshot: AnalysisRequest;
  snapshotHash: string;
  available: boolean;
}) {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<HeatmapMode>("standard");
  const [checking, setChecking] = useState(false);
  const [clusterError, setClusterError] = useState<string | null>(null);

  const toggle = async (checked: boolean) => {
    setClusterError(null);
    if (!checked) {
      setMode("standard");
      return;
    }
    setChecking(true);
    try {
      await queryClient.fetchQuery(
        chartQueryOptions(snapshot, snapshotHash, "heatmap", "cluster"),
      );
      setMode("cluster");
    } catch (error) {
      setClusterError(errorMessage(error));
      setMode("standard");
    } finally {
      setChecking(false);
    }
  };

  if (!available) {
    return (
      <p className="text-muted-foreground">{RESULTS_TEXT.NOT_AVAILABLE}</p>
    );
  }
  return (
    <div className="flex flex-col gap-3">
      <label className="flex w-fit items-center gap-2 text-sm">
        <Checkbox
          checked={mode === "cluster"}
          disabled={checking}
          onCheckedChange={(checked) => void toggle(checked)}
        />
        {RESULTS_TEXT.CLUSTER_CHECKBOX}
      </label>
      <InlineError message={clusterError} />
      <HeatmapImage
        snapshot={snapshot}
        snapshotHash={snapshotHash}
        mode={mode}
      />
    </div>
  );
}

function HeatmapImage({
  snapshot,
  snapshotHash,
  mode,
}: {
  snapshot: AnalysisRequest;
  snapshotHash: string;
  mode: HeatmapMode;
}) {
  const chart = useChart(snapshot, snapshotHash, "heatmap", mode);
  return (
    <ChartImage
      blob={chart.data}
      isPending={chart.isPending}
      error={chart.error}
      alt={TAB_LABELS.HEATMAP}
    />
  );
}
