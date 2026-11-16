import { useState } from "react";
import { ReviewRow } from "@/components/page-specific/analysis/ReviewRow";
import { StepFrame } from "@/components/page-specific/analysis/StepFrame";
import {
  FLOW_TEXT,
  REVIEW_LABELS,
  STEP_TEXT,
} from "@/constants/analysis.constants";
import { useCurrentRequest, useRunAnalysis } from "@/hooks/analysis.hook";
import type { StepId, StepProps } from "@/interfaces/analysis.interface";
import type { ScalesData } from "@/interfaces/scales.interface";
import { useAnalysisStore } from "@/store/analysis.store";
import { errorMessage } from "@/utils/api.utils";
import { matrixStepId } from "@/utils/flow.utils";
import { formatWeight } from "@/utils/format.utils";
import { validateNames } from "@/utils/validation.utils";

/** Off-diagonal cells that differ from the default. */
function editedCells(matrix: string[][], defaultLabel: string): number {
  return matrix.reduce(
    (total, row, i) =>
      total + row.filter((cell, j) => i !== j && cell !== defaultLabel).length,
    0,
  );
}

/** Every answer with an Edit link, and "Run Analysis" (validates, runs, opens Results). */
export function ReviewStep({
  scales,
  onOpen,
  ...nav
}: StepProps & { scales: ScalesData; onOpen: (step: StepId) => void }) {
  const state = useAnalysisStore();
  const request = useCurrentRequest();
  const run = useRunAnalysis();
  const [error, setError] = useState<string | null>(null);
  const labelOf = (options: ScalesData["solvers"], key: string | null) =>
    options.find((option) => option.key === key)?.label ?? key ?? "";

  const handleRun = () => {
    const message = validateNames(
      state.factors,
      state.experts.map((expert) => expert.name),
    );
    setError(message);
    if (message || !request) return;
    run.mutate(request, { onSuccess: nav.onAdvance });
  };

  return (
    <StepFrame
      number={nav.number}
      wide
      focusNext
      title={STEP_TEXT.review.title}
      help={STEP_TEXT.review.help}
      error={error ?? (run.error ? errorMessage(run.error) : null)}
      pending={run.isPending}
      nextLabel={run.isPending ? FLOW_TEXT.RUNNING : FLOW_TEXT.RUN}
      onNext={handleRun}
      onBack={nav.onBack}
    >
      <dl className="divide-y rounded-lg border bg-card px-4">
        <ReviewRow label={REVIEW_LABELS.SOLVER} onEdit={() => onOpen("solver")}>
          {labelOf(scales.solvers, state.solver)}
        </ReviewRow>
        <ReviewRow
          label={REVIEW_LABELS.THRESHOLD}
          onEdit={() => onOpen("threshold")}
        >
          {labelOf(scales.thresholds, state.threshold)}
        </ReviewRow>
        <ReviewRow
          label={REVIEW_LABELS.EXPERTS}
          onEdit={() => onOpen("expert-weights")}
        >
          {state.experts
            .map(
              (expert) =>
                `${expert.name} (${formatWeight(expert.weight, scales.weights.decimals)})`,
            )
            .join(", ")}
        </ReviewRow>
        <ReviewRow
          label={REVIEW_LABELS.FACTORS}
          onEdit={() => onOpen("factor-names")}
        >
          {state.factors.join(", ")}
        </ReviewRow>
        {state.experts.map((expert, index) => (
          <ReviewRow
            // biome-ignore lint/suspicious/noArrayIndexKey: experts are positional
            key={index}
            label={`${REVIEW_LABELS.MATRICES}: ${expert.name}`}
            onEdit={() => onOpen(matrixStepId(index))}
          >
            {REVIEW_LABELS.EDITED_CELLS(
              editedCells(
                state.matrices[index] ?? [],
                state.scale?.defaultLabel ?? "",
              ),
            )}
          </ReviewRow>
        ))}
      </dl>
    </StepFrame>
  );
}
