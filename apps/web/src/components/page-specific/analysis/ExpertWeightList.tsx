import { NumberStepper } from "@/components/general/NumberStepper";
import { Input } from "@/components/ui/input";
import { FIELD_LABELS } from "@/constants/analysis.constants";
import type { ScalesData } from "@/interfaces/scales.interface";
import { useAnalysisStore } from "@/store/analysis.store";

/** Name and weight (0–1, the API's step and decimals) per expert. */
export function ExpertWeightList({ scales }: { scales: ScalesData }) {
  const experts = useAnalysisStore((state) => state.experts);
  const setExpertName = useAnalysisStore((state) => state.setExpertName);
  const setExpertWeight = useAnalysisStore((state) => state.setExpertWeight);

  return (
    <ol className="flex flex-col gap-2">
      {experts.map((expert, index) => (
        // biome-ignore lint/suspicious/noArrayIndexKey: experts are positional
        <li key={index} className="flex flex-wrap items-center gap-2">
          <Input
            aria-label={FIELD_LABELS.EXPERT_NAME(index)}
            value={expert.name}
            className="min-w-40 flex-1"
            onChange={(event) => setExpertName(index, event.target.value)}
          />
          <NumberStepper
            id={`expert-weight-${index}`}
            label={FIELD_LABELS.EXPERT_WEIGHT(index)}
            value={expert.weight}
            min={0}
            max={1}
            step={scales.weights.step}
            decimals={scales.weights.decimals}
            onChange={(weight) => setExpertWeight(index, weight)}
          />
        </li>
      ))}
    </ol>
  );
}
