import { SUMMARY_TEXT } from "@/constants/results.constants";
import type { ResultSummary } from "@/interfaces/result.interface";
import { formatThreshold } from "@/utils/format.utils";

/** "Analysis Configuration": result type, threshold method label and value (4 dp or "—"). */
export function ConfigurationPanel({ summary }: { summary: ResultSummary }) {
  const rows = [
    [SUMMARY_TEXT.RESULT_TYPE, summary.result_type_label],
    [SUMMARY_TEXT.THRESHOLD_METHOD, summary.threshold_method_label],
    [SUMMARY_TEXT.THRESHOLD_VALUE, formatThreshold(summary.threshold_value)],
  ] as const;

  return (
    <section className="flex flex-col gap-3 rounded-lg bg-muted/60 p-4">
      <h3 className="font-semibold">{SUMMARY_TEXT.CONFIG_TITLE}</h3>
      <dl className="flex flex-col gap-2 text-sm">
        {rows.map(([label, value]) => (
          <div key={label} className="flex flex-wrap justify-between gap-2">
            <dt className="text-muted-foreground">{label}</dt>
            <dd className="font-medium">{value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
