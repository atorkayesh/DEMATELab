import { useVirtualizer } from "@tanstack/react-virtual";
import { useRef } from "react";
import { MatrixCell } from "@/components/page-specific/analysis/MatrixCell";
import { MATRIX_GRID } from "@/constants/analysis.constants";
import type { MatrixScale } from "@/interfaces/scales.interface";
import { cn } from "@/lib/utils";
import { useAnalysisStore } from "@/store/analysis.store";

/** Frozen factor-name column: narrower on phones so more cells fit. */
const ROW_HEADER_WIDTH = "w-24 sm:w-40";

const HEADER_CLASS =
  "flex items-center truncate px-2 text-xs font-semibold text-foreground";

/**
 * One expert's matrix: rows and columns virtualised so 100 × 100 stays responsive, with the factor
 * header row and column frozen (sticky). Rows are the influencing factors. The first editable cell
 * (row 1, column 2) is the step's initial focus.
 */
export function MatrixGrid({
  expert,
  terms,
  scale,
}: {
  expert: number;
  terms: readonly string[];
  scale: MatrixScale;
}) {
  const factors = useAnalysisStore((state) => state.factors);
  const scrollRef = useRef<HTMLDivElement>(null);
  const size = factors.length;
  const cellWidth = MATRIX_GRID.CELL_WIDTH[scale.family];

  const rows = useVirtualizer({
    count: size,
    getScrollElement: () => scrollRef.current,
    estimateSize: () => MATRIX_GRID.ROW_HEIGHT,
    overscan: MATRIX_GRID.OVERSCAN,
    initialRect: MATRIX_GRID.INITIAL_RECT,
  });
  const columns = useVirtualizer({
    horizontal: true,
    count: size,
    getScrollElement: () => scrollRef.current,
    estimateSize: () => cellWidth,
    overscan: MATRIX_GRID.OVERSCAN,
    initialRect: MATRIX_GRID.INITIAL_RECT,
  });
  const bodyWidth = columns.getTotalSize();
  const bodyHeight = rows.getTotalSize();
  const virtualRows = rows.getVirtualItems();
  const virtualColumns = columns.getVirtualItems();

  return (
    <div
      ref={scrollRef}
      className="max-h-[60vh] w-full overflow-auto rounded-lg border bg-card"
    >
      <div className="w-max">
        <div
          className="sticky top-0 z-20 flex border-b bg-card"
          style={{ height: MATRIX_GRID.HEADER_HEIGHT }}
        >
          <div
            className={cn(
              "sticky left-0 z-30 shrink-0 border-r bg-card",
              ROW_HEADER_WIDTH,
            )}
          />
          <div className="relative shrink-0" style={{ width: bodyWidth }}>
            {virtualColumns.map((column) => (
              <div
                key={column.key}
                title={factors[column.index]}
                className={`absolute top-0 h-full ${HEADER_CLASS}`}
                style={{ left: column.start, width: column.size }}
              >
                {factors[column.index]}
              </div>
            ))}
          </div>
        </div>
        <div className="flex" style={{ height: bodyHeight }}>
          <div
            className={cn(
              "sticky left-0 z-10 shrink-0 border-r bg-card",
              ROW_HEADER_WIDTH,
            )}
            style={{ height: bodyHeight }}
          >
            {virtualRows.map((row) => (
              <div
                key={row.key}
                title={factors[row.index]}
                className={`absolute left-0 w-full ${HEADER_CLASS}`}
                style={{ top: row.start, height: row.size }}
              >
                {factors[row.index]}
              </div>
            ))}
          </div>
          <div className="relative shrink-0" style={{ width: bodyWidth }}>
            {virtualRows.map((row) =>
              virtualColumns.map((column) => (
                <div
                  key={`${row.key}-${column.key}`}
                  className="absolute p-1"
                  style={{
                    top: row.start,
                    left: column.start,
                    width: column.size,
                    height: row.size,
                  }}
                >
                  <MatrixCell
                    expert={expert}
                    row={row.index}
                    column={column.index}
                    rowName={factors[row.index]}
                    columnName={factors[column.index]}
                    terms={terms}
                    defaultLabel={scale.defaultLabel}
                    autoFocus={row.index === 0 && column.index === 1}
                  />
                </div>
              )),
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
