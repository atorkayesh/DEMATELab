import { MatrixGrid } from "@/components/page-specific/analysis/MatrixGrid";
import { MatrixImportActions } from "@/components/page-specific/analysis/MatrixImportActions";
import { StepFrame } from "@/components/page-specific/analysis/StepFrame";
import {
  MATRIX_HELP,
  MATRIX_STEP_QUESTION,
  matrixStepTitle,
} from "@/constants/analysis.constants";
import { termsForScale } from "@/hooks/scales.hook";
import type { StepProps } from "@/interfaces/analysis.interface";
import type { ScalesData } from "@/interfaces/scales.interface";
import { useAnalysisStore } from "@/store/analysis.store";

/** One matrix step per expert: the import buttons and the expert's matrix. */
export function ExpertMatrixStep({
  expert,
  scales,
  ...nav
}: StepProps & { expert: number; scales: ScalesData }) {
  const scale = useAnalysisStore((state) => state.scale);
  const count = useAnalysisStore((state) => state.experts.length);
  const name = useAnalysisStore((state) => state.experts[expert]?.name ?? "");
  if (!scale) return null;

  return (
    <StepFrame
      number={nav.number}
      wide
      title={matrixStepTitle(expert, count, name)}
      help={
        <>
          {MATRIX_STEP_QUESTION} {MATRIX_HELP}
        </>
      }
      onNext={nav.onAdvance}
      onBack={nav.onBack}
    >
      <div className="flex flex-col gap-3">
        <MatrixImportActions
          expert={expert}
          showImportAll={expert === 0}
          isZ={scale.family === "fuzzy_z"}
        />
        <MatrixGrid
          expert={expert}
          terms={termsForScale(scales, scale)}
          scale={scale}
        />
      </div>
    </StepFrame>
  );
}
