import { ArrowLeftIcon } from "lucide-react";
import { SectionCard } from "@/components/general/SectionCard";
import { ExportBar } from "@/components/page-specific/analysis/ExportBar";
import { OutdatedResultsBanner } from "@/components/page-specific/analysis/OutdatedResultsBanner";
import { ResultTabs } from "@/components/page-specific/analysis/ResultTabs";
import { StartOverButton } from "@/components/page-specific/analysis/StartOverButton";
import { Button } from "@/components/ui/button";
import { FLOW_TEXT } from "@/constants/analysis.constants";
import { RESULTS_TEXT } from "@/constants/results.constants";
import { useAnalysisStore } from "@/store/analysis.store";

/** Full-width Results screen for the stored snapshot; "Back to inputs" opens Review, "Start over" clears everything. */
export function ResultsCard({ onBack }: { onBack: () => void }) {
  const snapshot = useAnalysisStore((state) => state.snapshot);
  const snapshotHash = useAnalysisStore((state) => state.snapshotHash);
  const data = useAnalysisStore((state) => state.results);
  if (!snapshot || !data) return null;

  return (
    <div className="flex w-full flex-col gap-4 pt-6 pb-8 duration-200 animate-in fade-in slide-in-from-bottom-3 motion-reduce:animate-none">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button
          type="button"
          variant="outline"
          className="max-sm:h-11"
          onClick={onBack}
        >
          <ArrowLeftIcon data-icon="inline-start" />
          {FLOW_TEXT.BACK_TO_INPUTS}
        </Button>
        <StartOverButton />
      </div>
      <SectionCard title={RESULTS_TEXT.TITLE} subtitle={RESULTS_TEXT.SUBTITLE}>
        <div className="flex flex-col gap-4">
          <OutdatedResultsBanner />
          <ExportBar snapshot={snapshot} data={data} />
          <ResultTabs
            key={snapshotHash}
            snapshot={snapshot}
            snapshotHash={snapshotHash}
            data={data}
          />
        </div>
      </SectionCard>
    </div>
  );
}
