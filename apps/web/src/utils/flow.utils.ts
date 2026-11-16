import { matrixStepLabel, STEP_TEXT } from "@/constants/analysis.constants";
import type { FixedStepId, StepId } from "@/interfaces/analysis.interface";

/** The question steps before the matrices. */
export const SETUP_STEPS: readonly FixedStepId[] = [
  "solver",
  "threshold",
  "experts",
  "factors",
  "factor-names",
  "expert-weights",
];

/** Step id of expert `index`'s matrix (0-based index, 1-based id). */
export function matrixStepId(index: number): StepId {
  return `matrix-${index + 1}`;
}

/** 0-based expert index of a matrix step, or null for other steps. */
export function matrixStepIndex(step: StepId): number | null {
  const match = /^matrix-(\d+)$/.exec(step);
  return match ? Number(match[1]) - 1 : null;
}

/** Question steps in order for `expertCount` experts (Results is not a question). */
export function questionSteps(expertCount: number): StepId[] {
  return [
    ...SETUP_STEPS,
    ...Array.from({ length: expertCount }, (_, i) => matrixStepId(i)),
    "review",
  ];
}

/** Whether `value` names a step that can exist (search param validation). */
export function isStepId(value: string): value is StepId {
  return (
    value === "review" ||
    value === "results" ||
    (SETUP_STEPS as readonly string[]).includes(value) ||
    /^matrix-[1-9]\d*$/.test(value)
  );
}

/**
 * The first step that is not answered yet: the farthest step the user may open.
 * Review counts as answered once results exist, so Results can open.
 */
export function firstUnansweredStep(
  steps: readonly StepId[],
  answered: ReadonlySet<StepId>,
): StepId {
  return steps.find((step) => !answered.has(step)) ?? "review";
}

/** Whether `step` can be opened: all earlier steps are answered (Results needs results). */
export function canOpenStep(
  step: StepId,
  steps: readonly StepId[],
  answered: ReadonlySet<StepId>,
  hasResults: boolean,
): boolean {
  if (step === "results") return hasResults;
  const index = steps.indexOf(step);
  if (index < 0) return false;
  return steps.slice(0, index).every((earlier) => answered.has(earlier));
}

/** The step after `step`, or Results after Review. */
export function nextStep(step: StepId, steps: readonly StepId[]): StepId {
  const index = steps.indexOf(step);
  return steps[index + 1] ?? "results";
}

/** The step before `step`; Results goes back to Review. */
export function previousStep(
  step: StepId,
  steps: readonly StepId[],
): StepId | null {
  if (step === "results") return "review";
  const index = steps.indexOf(step);
  return index > 0 ? steps[index - 1] : null;
}

/** Short label of a step for the step list. */
export function stepLabel(step: StepId): string {
  const index = matrixStepIndex(step);
  return index === null
    ? STEP_TEXT[step as FixedStepId].label
    : matrixStepLabel(index);
}
