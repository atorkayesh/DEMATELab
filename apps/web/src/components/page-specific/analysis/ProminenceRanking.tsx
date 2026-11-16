import { SUMMARY_TEXT } from "@/constants/results.constants";
import type { ResultSummary } from "@/interfaces/result.interface";
import { cn } from "@/lib/utils";
import { formatFixed, formatSigned } from "@/utils/format.utils";

/** Factors by prominence (the API's order), with a bar, "P x.xx" and "R ±x.xx". */
export function ProminenceRanking({ summary }: { summary: ResultSummary }) {
  return (
    <section className="flex flex-col gap-3 rounded-lg bg-muted/60 p-4">
      <h3 className="font-semibold">{SUMMARY_TEXT.RANKING_TITLE}</h3>
      <ol className="flex flex-col gap-2">
        {summary.prominence_ranking.map((item) => (
          <li
            key={item.factor}
            className="grid grid-cols-[minmax(0,8rem)_1fr_auto] items-center gap-3 text-sm"
          >
            <span className="truncate font-medium" title={item.factor}>
              {item.factor}
            </span>
            <span className="h-2 overflow-hidden rounded-full bg-soft-2">
              <span
                className={cn(
                  "block h-full rounded-full",
                  item.relation >= 0 ? "bg-cause" : "bg-effect",
                )}
                style={{ width: `${Math.max(0, item.bar_ratio) * 100}%` }}
              />
            </span>
            <span className="flex gap-3 whitespace-nowrap tabular-nums text-muted-foreground">
              <span>P {formatFixed(item.prominence, 2)}</span>
              <span>R {formatSigned(item.relation, 2)}</span>
            </span>
          </li>
        ))}
      </ol>
    </section>
  );
}
