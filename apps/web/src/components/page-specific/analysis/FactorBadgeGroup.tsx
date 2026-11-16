import { RESULTS_TEXT } from "@/constants/results.constants";
import { cn } from "@/lib/utils";

/** Cause or effect group as auto-width pills (long names are not clipped), "—" when empty. */
export function FactorBadgeGroup({
  title,
  factors,
  tone,
}: {
  title: string;
  factors: string[];
  tone: "cause" | "effect";
}) {
  return (
    <section className="flex flex-col gap-3 rounded-lg bg-muted/60 p-4">
      <h3 className="font-semibold">{title}</h3>
      {factors.length === 0 ? (
        <p className="text-muted-foreground">{RESULTS_TEXT.EMPTY_GROUP}</p>
      ) : (
        <ul className="flex flex-wrap gap-1.5">
          {factors.map((factor) => (
            <li
              key={factor}
              className={cn(
                "rounded-full px-2.5 py-0.5 text-xs font-semibold wrap-break-word",
                tone === "cause"
                  ? "bg-cause text-cause-foreground"
                  : "bg-effect text-effect-foreground",
              )}
            >
              {factor}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
