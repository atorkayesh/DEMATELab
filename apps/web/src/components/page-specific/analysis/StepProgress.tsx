import { FLOW_TEXT } from "@/constants/analysis.constants";

/** Thin bar showing how far through the questions the current step is. */
export function StepProgress({
  current,
  total,
}: {
  current: number;
  total: number;
}) {
  const percent = total > 0 ? Math.round((current / total) * 100) : 0;
  return (
    <div
      role="progressbar"
      aria-label={FLOW_TEXT.PROGRESS_LABEL}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={percent}
      className="h-1 w-full overflow-hidden rounded-full bg-soft-2"
    >
      <div
        className="h-full rounded-full bg-primary transition-[width] duration-200 motion-reduce:transition-none"
        style={{ width: `${percent}%` }}
      />
    </div>
  );
}
