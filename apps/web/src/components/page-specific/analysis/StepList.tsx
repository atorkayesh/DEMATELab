import { CheckIcon } from "lucide-react";
import { FLOW_TEXT } from "@/constants/analysis.constants";
import type { StepId } from "@/interfaces/analysis.interface";
import { cn } from "@/lib/utils";
import { stepLabel } from "@/utils/flow.utils";

/** Compact list of the steps; answered (and reachable) steps open on click. */
export function StepList({
  steps,
  current,
  answered,
  canOpen,
  onOpen,
}: {
  steps: readonly StepId[];
  current: StepId;
  answered: ReadonlySet<StepId>;
  canOpen: (step: StepId) => boolean;
  onOpen: (step: StepId) => void;
}) {
  return (
    <nav
      aria-label={FLOW_TEXT.STEPS_LABEL}
      className="w-full overflow-x-auto pb-1"
    >
      <ol className="mx-auto flex w-max gap-1.5">
        {steps.map((step, index) => {
          const isCurrent = step === current;
          const done = answered.has(step);
          return (
            <li key={step}>
              <button
                type="button"
                disabled={isCurrent || !canOpen(step)}
                aria-current={isCurrent ? "step" : undefined}
                onClick={() => onOpen(step)}
                className={cn(
                  "flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs max-sm:py-2 whitespace-nowrap transition-colors",
                  isCurrent
                    ? "border-primary bg-primary text-primary-foreground"
                    : "bg-card text-muted-foreground enabled:hover:text-foreground disabled:opacity-60",
                )}
              >
                {done && !isCurrent ? (
                  <CheckIcon className="size-3" aria-hidden="true" />
                ) : (
                  <span aria-hidden="true">{index + 1}.</span>
                )}
                {stepLabel(step)}
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
