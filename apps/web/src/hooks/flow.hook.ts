import { useMemo } from "react";
import type { StepId } from "@/interfaces/analysis.interface";
import { useAnalysisStore } from "@/store/analysis.store";
import { questionSteps } from "@/utils/flow.utils";

/** Ordered question steps for the current expert count, and which are answered. */
export function useFlowSteps() {
  const expertCount = useAnalysisStore((state) => state.expertCount);
  const answeredList = useAnalysisStore((state) => state.answered);
  const hasResults = useAnalysisStore((state) => state.results !== null);
  const steps = useMemo(() => questionSteps(expertCount ?? 0), [expertCount]);
  const answered = useMemo(() => new Set<StepId>(answeredList), [answeredList]);
  return { steps, answered, hasResults };
}
