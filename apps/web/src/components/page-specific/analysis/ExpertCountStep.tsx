import { useRef, useState } from "react";
import { NumberStepper } from "@/components/general/NumberStepper";
import { ResetConfirmDialog } from "@/components/page-specific/analysis/ResetConfirmDialog";
import { StepFrame } from "@/components/page-specific/analysis/StepFrame";
import { RESET_CONFIRM_TEXT, STEP_TEXT } from "@/constants/analysis.constants";
import { useDefaultWeights } from "@/hooks/analysis.hook";
import type { StepProps } from "@/interfaces/analysis.interface";
import type { ScalesData } from "@/interfaces/scales.interface";
import { useAnalysisStore } from "@/store/analysis.store";
import { errorMessage } from "@/utils/api.utils";
import { matrixHasEdits } from "@/utils/matrix.utils";

/**
 * Step 3: number of experts. Remaining experts keep names and matrices; the weights are reset to
 * the API's defaults for the new count. Removing experts with edited matrices asks first.
 */
export function ExpertCountStep({
  scales,
  ...nav
}: StepProps & { scales: ScalesData }) {
  const { limits } = scales;
  const stored = useAnalysisStore((state) => state.expertCount);
  const setExpertCount = useAnalysisStore((state) => state.setExpertCount);
  const [count, setCount] = useState(stored ?? limits.experts_default);
  // Enter commits the stepper and continues in one event, before `count` re-renders.
  const latest = useRef(count);
  const [confirming, setConfirming] = useState(false);
  const defaults = useDefaultWeights();

  const commit = () => {
    const next = latest.current;
    defaults.mutate(next, {
      onSuccess: (weights) => {
        setExpertCount(next, weights);
        nav.onAdvance();
      },
    });
  };

  const handleNext = () => {
    if (latest.current === stored) {
      nav.onAdvance();
      return;
    }
    const { matrices, scale } = useAnalysisStore.getState();
    const losesEdits =
      scale !== null &&
      matrices
        .slice(latest.current)
        .some((matrix) => matrixHasEdits(matrix, scale.defaultLabel));
    if (losesEdits) setConfirming(true);
    else commit();
  };

  return (
    <StepFrame
      number={nav.number}
      title={STEP_TEXT.experts.title}
      help={STEP_TEXT.experts.help}
      error={defaults.error ? errorMessage(defaults.error) : null}
      pending={defaults.isPending}
      onNext={handleNext}
      onBack={nav.onBack}
    >
      <NumberStepper
        id="expert-count"
        label={STEP_TEXT.experts.title}
        value={count}
        min={limits.experts_min}
        max={limits.experts_max}
        onChange={(next) => {
          latest.current = next;
          setCount(next);
        }}
      />
      <ResetConfirmDialog
        open={confirming}
        paragraphs={[RESET_CONFIRM_TEXT.EXPERTS]}
        onConfirm={() => {
          setConfirming(false);
          commit();
        }}
        onCancel={() => setConfirming(false)}
      />
    </StepFrame>
  );
}
