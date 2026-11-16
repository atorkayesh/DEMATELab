import { RefreshCwIcon } from "lucide-react";
import { useState } from "react";
import { InlineError } from "@/components/general/InlineError";
import { Button } from "@/components/ui/button";
import { RESULTS_TEXT } from "@/constants/results.constants";
import {
  useCurrentRequest,
  useResultsOutdated,
  useRunAnalysis,
} from "@/hooks/analysis.hook";
import { useAnalysisStore } from "@/store/analysis.store";
import { errorMessage } from "@/utils/api.utils";
import { validateNames } from "@/utils/validation.utils";

/** Shown when the answers changed after the run; "Re-run" analyses the current answers. */
export function OutdatedResultsBanner() {
  const outdated = useResultsOutdated();
  const request = useCurrentRequest();
  const run = useRunAnalysis();
  const [error, setError] = useState<string | null>(null);
  if (!outdated) return null;

  const rerun = () => {
    const { factors, experts } = useAnalysisStore.getState();
    const message = validateNames(
      factors,
      experts.map((expert) => expert.name),
    );
    setError(message);
    if (!message && request) run.mutate(request);
  };

  return (
    <output className="flex flex-col gap-2 rounded-lg border border-line-strong bg-muted px-4 py-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm font-medium">{RESULTS_TEXT.OUTDATED}</p>
        <Button
          type="button"
          size="sm"
          onClick={rerun}
          disabled={run.isPending}
        >
          <RefreshCwIcon
            data-icon="inline-start"
            className={run.isPending ? "animate-spin" : undefined}
          />
          {RESULTS_TEXT.RERUN}
        </Button>
      </div>
      <InlineError
        message={error ?? (run.error ? errorMessage(run.error) : null)}
      />
    </output>
  );
}
