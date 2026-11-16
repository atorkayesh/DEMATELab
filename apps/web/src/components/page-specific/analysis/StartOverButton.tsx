import { useNavigate } from "@tanstack/react-router";
import { RotateCcwIcon } from "lucide-react";
import { useState } from "react";
import { ResetConfirmDialog } from "@/components/page-specific/analysis/ResetConfirmDialog";
import { Button } from "@/components/ui/button";
import { START_OVER_TEXT } from "@/constants/analysis.constants";
import { useAnalysisStore } from "@/store/analysis.store";

/**
 * Quiet "Start over" action: after confirmation, clears every answer, matrix and result and opens
 * the first step. Hidden while there is nothing to clear.
 */
export function StartOverButton({ disabled = false }: { disabled?: boolean }) {
  const navigate = useNavigate({ from: "/" });
  const hasData = useAnalysisStore(
    (state) => state.answered.length > 0 || state.results !== null,
  );
  const reset = useAnalysisStore((state) => state.reset);
  const [confirming, setConfirming] = useState(false);
  if (!hasData) return null;

  const startOver = () => {
    setConfirming(false);
    reset();
    navigate({ search: { step: "solver" } });
  };

  return (
    <>
      <Button
        type="button"
        variant="ghost"
        className="text-muted-foreground max-sm:h-11 hover:bg-transparent aria-expanded:bg-transparent hover:text-destructive focus-visible:text-destructive"
        onClick={() => setConfirming(true)}
        disabled={disabled}
      >
        <RotateCcwIcon data-icon="inline-start" />
        {START_OVER_TEXT.BUTTON}
      </Button>
      <ResetConfirmDialog
        open={confirming}
        title={START_OVER_TEXT.TITLE}
        paragraphs={[START_OVER_TEXT.DESCRIPTION]}
        confirmLabel={START_OVER_TEXT.CONFIRM}
        cancelLabel={START_OVER_TEXT.CANCEL}
        onConfirm={startOver}
        onCancel={() => setConfirming(false)}
      />
    </>
  );
}
