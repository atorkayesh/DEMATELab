import { useRef, useState } from "react";
import { NumberStepper } from "@/components/general/NumberStepper";
import { ResetConfirmDialog } from "@/components/page-specific/analysis/ResetConfirmDialog";
import { StepFrame } from "@/components/page-specific/analysis/StepFrame";
import { RESET_CONFIRM_TEXT, STEP_TEXT } from "@/constants/analysis.constants";
import type { StepProps } from "@/interfaces/analysis.interface";
import type { ScalesData } from "@/interfaces/scales.interface";
import { useAnalysisStore } from "@/store/analysis.store";
import { resizeLosesEdits } from "@/utils/matrix.utils";

/**
 * Step 4: number of factors. Remaining factors keep names and cells; new ones get `F{i}` and
 * default cells. Removing factors whose rows or columns hold edited cells asks first.
 */
export function FactorCountStep({
  scales,
  ...nav
}: StepProps & { scales: ScalesData }) {
  const { limits } = scales;
  const stored = useAnalysisStore((state) => state.factorCount);
  const setFactorCount = useAnalysisStore((state) => state.setFactorCount);
  const [count, setCount] = useState(stored ?? limits.factors_default);
  // Enter commits the stepper and continues in one event, before `count` re-renders.
  const latest = useRef(count);
  const [confirming, setConfirming] = useState(false);

  const commit = () => {
    setFactorCount(latest.current);
    nav.onAdvance();
  };
  const handleNext = () => {
    const { matrices, scale } = useAnalysisStore.getState();
    const losesEdits =
      scale !== null &&
      matrices.some((matrix) =>
        resizeLosesEdits(matrix, latest.current, scale.defaultLabel),
      );
    if (losesEdits) setConfirming(true);
    else commit();
  };

  return (
    <StepFrame
      number={nav.number}
      title={STEP_TEXT.factors.title}
      help={STEP_TEXT.factors.help}
      onNext={handleNext}
      onBack={nav.onBack}
    >
      <NumberStepper
        id="factor-count"
        label={STEP_TEXT.factors.title}
        value={count}
        min={limits.factors_min}
        max={limits.factors_max}
        onChange={(next) => {
          latest.current = next;
          setCount(next);
        }}
      />
      <ResetConfirmDialog
        open={confirming}
        paragraphs={[RESET_CONFIRM_TEXT.FACTORS]}
        onConfirm={() => {
          setConfirming(false);
          commit();
        }}
        onCancel={() => setConfirming(false)}
      />
    </StepFrame>
  );
}
