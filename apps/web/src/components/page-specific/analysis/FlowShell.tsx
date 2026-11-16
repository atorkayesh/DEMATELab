import { Navigate, useNavigate, useSearch } from "@tanstack/react-router";
import { FlowStep } from "@/components/page-specific/analysis/FlowStep";
import { ResultsCard } from "@/components/page-specific/analysis/ResultsCard";
import { StepList } from "@/components/page-specific/analysis/StepList";
import { StepProgress } from "@/components/page-specific/analysis/StepProgress";
import { Button } from "@/components/ui/button";
import { FLOW_TEXT } from "@/constants/analysis.constants";
import { useFlowSteps } from "@/hooks/flow.hook";
import { useScales } from "@/hooks/scales.hook";
import type { StepId } from "@/interfaces/analysis.interface";
import type { ScalesData } from "@/interfaces/scales.interface";
import { useAnalysisStore } from "@/store/analysis.store";
import {
  canOpenStep,
  firstUnansweredStep,
  isStepId,
  nextStep,
  previousStep,
} from "@/utils/flow.utils";

/** The `/` page: loads the scales, then runs the one-question-per-step flow. */
export function FlowShell() {
  const scales = useScales();

  if (scales.isPending) {
    return <p className="pt-16 text-muted-foreground">{FLOW_TEXT.LOADING}</p>;
  }
  if (scales.isError) {
    return (
      <div role="alert" className="flex flex-col items-center gap-3 pt-16">
        <p className="text-destructive">{FLOW_TEXT.LOAD_FAILED}</p>
        <Button
          type="button"
          variant="outline"
          onClick={() => scales.refetch()}
        >
          {FLOW_TEXT.RETRY}
        </Button>
      </div>
    );
  }
  return <Flow scales={scales.data} />;
}

/**
 * The current step from the `step` search param (so browser Back/Forward move between steps). A
 * step whose earlier steps are not answered redirects to the first unanswered one.
 */
function Flow({ scales }: { scales: ScalesData }) {
  const { step: requested } = useSearch({ from: "/" });
  const navigate = useNavigate({ from: "/" });
  const markAnswered = useAnalysisStore((state) => state.markAnswered);
  const { steps, answered, hasResults } = useFlowSteps();
  const canOpen = (step: StepId) =>
    canOpenStep(step, steps, answered, hasResults);

  const step = requested && isStepId(requested) ? requested : null;
  if (!step || !canOpen(step)) {
    return (
      <Navigate
        to="/"
        search={{ step: firstUnansweredStep(steps, answered) }}
        replace
      />
    );
  }

  const goTo = (target: StepId) => navigate({ search: { step: target } });
  const previous = previousStep(step, steps);
  const back = previous ? () => goTo(previous) : null;

  if (step === "results") {
    return <ResultsCard onBack={() => goTo("review")} />;
  }

  const index = steps.indexOf(step);
  const advance = () => {
    markAnswered(step);
    goTo(nextStep(step, steps));
  };

  return (
    <div className="flex w-full flex-col items-center gap-6 pt-6 pb-8">
      <div className="flex w-full max-w-layout flex-col gap-3">
        <StepProgress current={index} total={steps.length} />
        <StepList
          steps={steps}
          current={step}
          answered={answered}
          canOpen={canOpen}
          onOpen={goTo}
        />
      </div>
      <div className="flex w-full justify-center pt-4 sm:pt-10">
        <FlowStep
          key={step}
          step={step}
          scales={scales}
          number={index + 1}
          onAdvance={advance}
          onBack={back}
          onOpen={goTo}
        />
      </div>
    </div>
  );
}
