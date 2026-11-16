import { ArrowLeftIcon, CheckIcon, LoaderCircleIcon } from "lucide-react";
import { StartOverButton } from "@/components/page-specific/analysis/StartOverButton";
import { Button } from "@/components/ui/button";
import { FLOW_TEXT } from "@/constants/analysis.constants";

/** Back and OK/Next under a question, Start over at the far end; OK submits the step's form (Enter does the same). */
export function StepNavigation({
  onBack,
  nextLabel = FLOW_TEXT.NEXT,
  pending,
  autoFocus = false,
}: {
  onBack: (() => void) | null;
  nextLabel?: string;
  pending: boolean;
  /** Mark OK as the step's initial focus (see StepFrame). */
  autoFocus?: boolean;
}) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <Button
        type="button"
        variant="outline"
        size="lg"
        onClick={() => onBack?.()}
        disabled={!onBack || pending}
      >
        <ArrowLeftIcon data-icon="inline-start" />
        {FLOW_TEXT.BACK}
      </Button>
      <Button
        type="submit"
        size="lg"
        disabled={pending}
        aria-busy={pending}
        data-autofocus={autoFocus || undefined}
      >
        {pending ? (
          <LoaderCircleIcon className="animate-spin" data-icon="inline-start" />
        ) : (
          <CheckIcon data-icon="inline-start" />
        )}
        {nextLabel}
      </Button>
      <span className="hidden text-xs text-muted-foreground sm:inline">
        {FLOW_TEXT.KEYBOARD_HINT}
      </span>
      <div className="ml-auto">
        <StartOverButton disabled={pending} />
      </div>
    </div>
  );
}
