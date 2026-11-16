import { useState } from "react";
import { FactorNameList } from "@/components/page-specific/analysis/FactorNameList";
import { StepFrame } from "@/components/page-specific/analysis/StepFrame";
import { STEP_TEXT } from "@/constants/analysis.constants";
import type { StepProps } from "@/interfaces/analysis.interface";
import { useAnalysisStore } from "@/store/analysis.store";
import { validateFactorNames } from "@/utils/validation.utils";

/** Step 5: factor names, checked with Qt's rules (filled, unique) on OK. */
export function FactorNamesStep(nav: StepProps) {
  const [error, setError] = useState<string | null>(null);

  return (
    <StepFrame
      number={nav.number}
      title={STEP_TEXT["factor-names"].title}
      help={STEP_TEXT["factor-names"].help}
      error={error}
      onNext={() => {
        const message = validateFactorNames(
          useAnalysisStore.getState().factors,
        );
        setError(message);
        if (!message) nav.onAdvance();
      }}
      onBack={nav.onBack}
    >
      <FactorNameList />
    </StepFrame>
  );
}
