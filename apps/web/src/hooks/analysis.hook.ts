import { useMutation } from "@tanstack/react-query";
import { useMemo } from "react";
import { useShallow } from "zustand/react/shallow";
import { MUTATION_KEYS } from "@/constants/query.constants";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import { runAnalysis } from "@/services/analysis.service";
import {
  getDefaultWeights,
  normalizeWeights,
} from "@/services/weights.service";
import { useAnalysisStore } from "@/store/analysis.store";
import {
  buildAnalysisRequest,
  requestKey,
} from "@/utils/analysis-request.utils";

export function useDefaultWeights() {
  return useMutation({
    mutationKey: MUTATION_KEYS.DEFAULT_WEIGHTS,
    mutationFn: getDefaultWeights,
  });
}

export function useNormalizeWeights() {
  return useMutation({
    mutationKey: MUTATION_KEYS.NORMALIZE_WEIGHTS,
    mutationFn: normalizeWeights,
  });
}

/** Run the analysis and store the results with the request they were computed from. */
export function useRunAnalysis() {
  const setResults = useAnalysisStore((state) => state.setResults);
  return useMutation({
    mutationKey: MUTATION_KEYS.RUN_ANALYSIS,
    mutationFn: runAnalysis,
    onSuccess: (data, request: AnalysisRequest) => setResults(request, data),
  });
}

/** The request for the current answers (null while the setup is incomplete). */
export function useCurrentRequest(): AnalysisRequest | null {
  const inputs = useAnalysisStore(
    useShallow((state) => ({
      solver: state.solver,
      threshold: state.threshold,
      factors: state.factors,
      experts: state.experts,
      matrices: state.matrices,
    })),
  );
  return useMemo(() => buildAnalysisRequest(inputs), [inputs]);
}

/** Whether the answers changed since the results were computed. */
export function useResultsOutdated(): boolean {
  const current = useCurrentRequest();
  const snapshot = useAnalysisStore((state) => state.snapshot);
  return useMemo(
    () => snapshot !== null && requestKey(current) !== requestKey(snapshot),
    [current, snapshot],
  );
}
