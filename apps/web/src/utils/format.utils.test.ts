import { describe, expect, it } from "vitest";
import {
  formatFixed,
  formatResultValue,
  formatSigned,
  formatThreshold,
  formatWeight,
} from "@/utils/format.utils";

describe("format utils", () => {
  it("formats crisp values with 4 decimals and tuples in parentheses", () => {
    expect(formatResultValue(0.123456)).toBe("0.1235");
    expect(formatResultValue([0.1, 0.2, 0.3])).toBe("(0.1000, 0.2000, 0.3000)");
    expect(formatResultValue([1, 2])).toBe("(1.0000, 2.0000)");
  });

  it("signs positive values and zero, as Qt", () => {
    expect(formatSigned(0.256, 2)).toBe("+0.26");
    expect(formatSigned(0, 2)).toBe("+0.00");
    expect(formatSigned(-1.234, 2)).toBe("-1.23");
  });

  it("shows an em dash for a missing threshold", () => {
    expect(formatThreshold(null)).toBe("—");
    expect(formatThreshold(0.1)).toBe("0.1000");
  });

  it("formats fixed decimals and weights", () => {
    expect(formatFixed(2, 2)).toBe("2.00");
    expect(formatWeight(0.5, 3)).toBe("0.500");
  });
});
