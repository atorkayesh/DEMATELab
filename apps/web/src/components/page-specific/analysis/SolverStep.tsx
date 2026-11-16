import { useState } from "react";
import { ChoiceList } from "@/components/page-specific/analysis/ChoiceList";
import { SolverChangeDialog } from "@/components/page-specific/analysis/SolverChangeDialog";
import { StepFrame } from "@/components/page-specific/analysis/StepFrame";
import { STEP_TEXT } from "@/constants/analysis.constants";
import { scaleForSolver } from "@/hooks/scales.hook";
import type { StepProps } from "@/interfaces/analysis.interface";
import type { ScalesData } from "@/interfaces/scales.interface";
import { useAnalysisStore } from "@/store/analysis.store";

/**
 * Step 1: the solver. Switching between the standard and Z families once matrices exist asks
 * first (Qt's warning); OK resets every matrix, Cancel restores the previous solver.
 */
export function SolverStep({
  scales,
  ...nav
}: StepProps & { scales: ScalesData }) {
  const stored = useAnalysisStore((state) => state.solver);
  const currentScale = useAnalysisStore((state) => state.scale);
  const hasMatrices = useAnalysisStore((state) => state.matrices.length > 0);
  const setSolver = useAnalysisStore((state) => state.setSolver);
  const [choice, setChoice] = useState(stored ?? scales.solvers[0]?.key ?? "");
  const [confirming, setConfirming] = useState(false);
  const scale = scaleForSolver(scales, choice);

  const commit = () => {
    setSolver(choice, scale);
    nav.onAdvance();
  };
  const handleNext = () => {
    if (hasMatrices && currentScale && currentScale.family !== scale.family) {
      setConfirming(true);
      return;
    }
    commit();
  };

  return (
    <StepFrame
      number={nav.number}
      title={STEP_TEXT.solver.title}
      help={STEP_TEXT.solver.help}
      onNext={handleNext}
      onBack={nav.onBack}
    >
      <ChoiceList
        name="solver"
        label={STEP_TEXT.solver.title}
        options={scales.solvers}
        value={choice}
        onChange={setChoice}
      />
      <SolverChangeDialog
        open={confirming}
        toZ={scale.family === "fuzzy_z"}
        onConfirm={() => {
          setConfirming(false);
          commit();
        }}
        onCancel={() => {
          setConfirming(false);
          if (stored) setChoice(stored);
        }}
      />
    </StepFrame>
  );
}
