import { describe, expect, it } from "vitest";
import type { StepId } from "@/interfaces/analysis.interface";
import {
  canOpenStep,
  firstUnansweredStep,
  isStepId,
  matrixStepIndex,
  nextStep,
  previousStep,
  questionSteps,
  stepLabel,
} from "@/utils/flow.utils";

const steps = questionSteps(2);

describe("flow utils", () => {
  it("lists the setup steps, one matrix step per expert, then review", () => {
    expect(steps).toEqual([
      "solver",
      "threshold",
      "experts",
      "factors",
      "factor-names",
      "expert-weights",
      "matrix-1",
      "matrix-2",
      "review",
    ]);
    expect(stepLabel("matrix-2")).toBe("Matrix 2");
    expect(matrixStepIndex("matrix-2")).toBe(1);
    expect(matrixStepIndex("review")).toBeNull();
  });

  it("validates step ids", () => {
    expect(isStepId("matrix-3")).toBe(true);
    expect(isStepId("matrix-0")).toBe(false);
    expect(isStepId("nope")).toBe(false);
  });

  it("opens a step only when every earlier step is answered", () => {
    const answered = new Set<StepId>(["solver", "threshold"]);
    expect(canOpenStep("experts", steps, answered, false)).toBe(true);
    expect(canOpenStep("factors", steps, answered, false)).toBe(false);
    expect(firstUnansweredStep(steps, answered)).toBe("experts");
  });

  it("opens results only when there are results", () => {
    expect(canOpenStep("results", steps, new Set(), false)).toBe(false);
    expect(canOpenStep("results", steps, new Set(), true)).toBe(true);
  });

  it("moves forward and back, Review → Results → Review", () => {
    expect(nextStep("expert-weights", steps)).toBe("matrix-1");
    expect(nextStep("review", steps)).toBe("results");
    expect(previousStep("results", steps)).toBe("review");
    expect(previousStep("solver", steps)).toBeNull();
  });
});
