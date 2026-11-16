import { ROW_STATE_DISPLAY } from "@/constants/health.constants";
import type { RowState } from "@/interfaces/health.interface";
import { cn } from "@/lib/utils";

/** One system: a coloured dot, its name and description, and its state on the right. */
export function StatusRow({
  label,
  description,
  state,
}: {
  label: string;
  description?: string;
  state: RowState;
}) {
  const display = ROW_STATE_DISPLAY[state];

  return (
    <div data-state={state} className="flex items-center gap-3 py-3.5">
      <span
        aria-hidden="true"
        className={cn("size-2.5 shrink-0 rounded-full", display.dotClass)}
      />
      <div className="flex min-w-0 flex-1 flex-wrap items-baseline gap-x-2.5 gap-y-0.5">
        <span className="font-medium text-foreground">{label}</span>
        {description && (
          <span className="text-muted-foreground wrap-break-word">
            {description}
          </span>
        )}
      </div>
      <span className="shrink-0 text-muted-foreground">{display.label}</span>
    </div>
  );
}
