import { ExpertCountStep } from "@/components/page-specific/analysis/ExpertCountStep";
import { ExpertMatrixStep } from "@/components/page-specific/analysis/ExpertMatrixStep";
import { ExpertWeightsStep } from "@/components/page-specific/analysis/ExpertWeightsStep";
import { FactorCountStep } from "@/components/page-specific/analysis/FactorCountStep";
import { FactorNamesStep } from "@/components/page-specific/analysis/FactorNamesStep";
import { ReviewStep } from "@/components/page-specific/analysis/ReviewStep";
import { SolverStep } from "@/components/page-specific/analysis/SolverStep";
import { ThresholdStep } from "@/components/page-specific/analysis/ThresholdStep";
import type { StepId, StepProps } from "@/interfaces/analysis.interface";
import type { ScalesData } from "@/interfaces/scales.interface";
import { matrixStepIndex } from "@/utils/flow.utils";

/** The question component of `step`. */
export function FlowStep({
  step,
  scales,
  onOpen,
  ...nav
}: StepProps & {
  step: StepId;
  scales: ScalesData;
  onOpen: (step: StepId) => void;
}) {
  switch (step) {
    case "solver":
      return <SolverStep scales={scales} {...nav} />;
    case "threshold":
      return <ThresholdStep scales={scales} {...nav} />;
    case "experts":
      return <ExpertCountStep scales={scales} {...nav} />;
    case "factors":
      return <FactorCountStep scales={scales} {...nav} />;
    case "factor-names":
      return <FactorNamesStep {...nav} />;
    case "expert-weights":
      return <ExpertWeightsStep scales={scales} {...nav} />;
    case "review":
      return <ReviewStep scales={scales} onOpen={onOpen} {...nav} />;
    default: {
      const expert = matrixStepIndex(step);
      return expert === null ? null : (
        <ExpertMatrixStep expert={expert} scales={scales} {...nav} />
      );
    }
  }
}
