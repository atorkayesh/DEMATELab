import { memo } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { useAnalysisStore } from "@/store/analysis.store";

/**
 * One judgement as a themed shadcn select. It subscribes to its own cell only, so changing a cell
 * re-renders that cell and not the grid. Cells that differ from the default are highlighted; the
 * diagonal is fixed.
 */
export const MatrixCell = memo(function MatrixCell({
  expert,
  row,
  column,
  rowName,
  columnName,
  terms,
  defaultLabel,
  autoFocus = false,
}: {
  expert: number;
  row: number;
  column: number;
  rowName: string;
  columnName: string;
  terms: readonly string[];
  defaultLabel: string;
  /** The step's initial focus (see StepFrame). */
  autoFocus?: boolean;
}) {
  const value = useAnalysisStore(
    (state) => state.matrices[expert]?.[row]?.[column] ?? defaultLabel,
  );
  const setCell = useAnalysisStore((state) => state.setCell);
  const diagonal = row === column;
  const edited = !diagonal && value !== defaultLabel;

  const options = terms.includes(value) ? terms : [value, ...terms];

  return (
    <Select
      value={value}
      disabled={diagonal}
      onValueChange={(next) => {
        if (typeof next === "string") setCell(expert, row, column, next);
      }}
    >
      <SelectTrigger
        aria-label={`${rowName} → ${columnName}`}
        data-edited={edited || undefined}
        data-autofocus={autoFocus || undefined}
        className={cn(
          "h-full w-full rounded-md bg-card px-1.5 text-base sm:text-sm disabled:bg-muted disabled:text-muted-foreground disabled:opacity-100",
          edited && "bg-cell-edited font-medium",
        )}
      >
        <SelectValue className="truncate" />
      </SelectTrigger>
      <SelectContent alignItemWithTrigger={false} className="min-w-44">
        {options.map((term) => (
          <SelectItem key={term} value={term} className="text-base sm:text-sm">
            {term}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
});
