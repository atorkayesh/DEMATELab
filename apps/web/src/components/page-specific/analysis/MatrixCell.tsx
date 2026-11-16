import { memo } from "react";
import { cn } from "@/lib/utils";
import { useAnalysisStore } from "@/store/analysis.store";

/**
 * One judgement as a native select. It subscribes to its own cell only, so changing a cell
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

  return (
    <select
      aria-label={`${rowName} → ${columnName}`}
      value={value}
      disabled={diagonal}
      data-edited={edited || undefined}
      data-autofocus={autoFocus || undefined}
      onChange={(event) => setCell(expert, row, column, event.target.value)}
      className={cn(
        "h-full w-full truncate rounded-md border border-input bg-card px-1.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:bg-muted disabled:text-muted-foreground",
        edited && "bg-cell-edited font-medium",
      )}
    >
      {!terms.includes(value) && <option value={value}>{value}</option>}
      {terms.map((term) => (
        <option key={term} value={term}>
          {term}
        </option>
      ))}
    </select>
  );
});
