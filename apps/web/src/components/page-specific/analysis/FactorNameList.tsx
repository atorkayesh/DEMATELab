import { Input } from "@/components/ui/input";
import { FIELD_LABELS } from "@/constants/analysis.constants";
import { useAnalysisStore } from "@/store/analysis.store";

/** One name field per factor, prefilled `F1..Fn`; edits rename the factor in place. */
export function FactorNameList() {
  const factors = useAnalysisStore((state) => state.factors);
  const setFactorName = useAnalysisStore((state) => state.setFactorName);

  return (
    <ol className="grid gap-2 sm:grid-cols-2">
      {factors.map((name, index) => (
        // Factors are positional: the index is the identity.
        // biome-ignore lint/suspicious/noArrayIndexKey: positional list
        <li key={index} className="flex items-center gap-2">
          <span className="w-8 shrink-0 text-right text-sm text-muted-foreground">
            {index + 1}.
          </span>
          <Input
            aria-label={FIELD_LABELS.FACTOR_NAME(index)}
            value={name}
            onChange={(event) => setFactorName(index, event.target.value)}
          />
        </li>
      ))}
    </ol>
  );
}
