import { describe, expect, it } from "vitest";
import { clampStepperValue } from "@/utils/stepper.utils";

describe("clampStepperValue", () => {
  it("clamps to the range", () => {
    expect(clampStepperValue("500", 1, 50, 0)).toBe(50);
    expect(clampStepperValue("0", 1, 50, 0)).toBe(1);
  });

  it("resets non-numbers and non-integers to the minimum", () => {
    expect(clampStepperValue("abc", 2, 100, 0)).toBe(2);
    expect(clampStepperValue("", 2, 100, 0)).toBe(2);
    expect(clampStepperValue("3.5", 2, 100, 0)).toBe(2);
  });

  it("rounds decimal values", () => {
    expect(clampStepperValue("0.33333", 0, 1, 3)).toBe(0.333);
    expect(clampStepperValue("1.5", 0, 1, 3)).toBe(1);
  });
});
