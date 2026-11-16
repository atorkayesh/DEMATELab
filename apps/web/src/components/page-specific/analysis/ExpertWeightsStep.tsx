import { useState } from "react";
import { ExpertWeightList } from "@/components/page-specific/analysis/ExpertWeightList";
import { StepFrame } from "@/components/page-specific/analysis/StepFrame";
import { FLOW_TEXT, STEP_TEXT } from "@/constants/analysis.constants";
import { useNormalizeWeights } from "@/hooks/analysis.hook";
import type { StepProps } from "@/interfaces/analysis.interface";
import type { ScalesData } from "@/interfaces/scales.interface";
import { useAnalysisStore } from "@/store/analysis.store";
import { errorMessage } from "@/utils/api.utils";
import { validateExpertNames } from "@/utils/validation.utils";

/**
 * Step 6: expert names and weights. OK checks the names, then lets the API check and correct the
 * weights (Qt's rule) and writes the corrected weights back into the fields.
 */
export function ExpertWeightsStep({
  scales,
  ...nav
}: StepProps & { scales: ScalesData }) {
  const weightsReset = useAnalysisStore((state) => state.weightsReset);
  const applyCorrectedWeights = useAnalysisStore(
    (state) => state.applyCorrectedWeights,
  );
  const clearWeightsReset = useAnalysisStore(
    (state) => state.clearWeightsReset,
  );
  const normalize = useNormalizeWeights();
  const [nameError, setNameError] = useState<string | null>(null);

  const handleNext = () => {
    const { experts } = useAnalysisStore.getState();
    const message = validateExpertNames(experts.map((expert) => expert.name));
    setNameError(message);
    if (message) return;
    normalize.mutate(
      experts.map((expert) => expert.weight),
      {
        onSuccess: (weights) => {
          applyCorrectedWeights(weights);
          clearWeightsReset();
          nav.onAdvance();
        },
      },
    );
  };

  return (
    <StepFrame
      number={nav.number}
      title={STEP_TEXT["expert-weights"].title}
      help={STEP_TEXT["expert-weights"].help}
      error={
        nameError ?? (normalize.error ? errorMessage(normalize.error) : null)
      }
      pending={normalize.isPending}
      onNext={handleNext}
      onBack={nav.onBack}
    >
      {weightsReset && (
        <p className="mb-3 rounded-lg bg-muted px-3 py-2 text-sm text-muted-foreground">
          {FLOW_TEXT.WEIGHTS_RESET_NOTE}
        </p>
      )}
      <ExpertWeightList scales={scales} />
    </StepFrame>
  );
}
