import { useState } from "react";
import { ChoiceList } from "@/components/page-specific/analysis/ChoiceList";
import { StepFrame } from "@/components/page-specific/analysis/StepFrame";
import { STEP_TEXT } from "@/constants/analysis.constants";
import type { StepProps } from "@/interfaces/analysis.interface";
import type { ScalesData } from "@/interfaces/scales.interface";
import { useAnalysisStore } from "@/store/analysis.store";

/** Step 2: the threshold method (matrices are kept when it changes). */
export function ThresholdStep({
  scales,
  ...nav
}: StepProps & { scales: ScalesData }) {
  const stored = useAnalysisStore((state) => state.threshold);
  const setThreshold = useAnalysisStore((state) => state.setThreshold);
  const [choice, setChoice] = useState(
    stored ?? scales.thresholds[0]?.key ?? "",
  );

  return (
    <StepFrame
      number={nav.number}
      title={STEP_TEXT.threshold.title}
      help={STEP_TEXT.threshold.help}
      onNext={() => {
        setThreshold(choice);
        nav.onAdvance();
      }}
      onBack={nav.onBack}
    >
      <ChoiceList
        name="threshold"
        label={STEP_TEXT.threshold.title}
        options={scales.thresholds}
        value={choice}
        onChange={setChoice}
      />
    </StepFrame>
  );
}
