import { describe, expect, it } from "vitest";
import {
  validateExpertNames,
  validateFactorNames,
  validateNames,
} from "@/utils/validation.utils";

describe("validation utils", () => {
  it("requires every factor name after trimming", () => {
    expect(validateFactorNames(["A", "  "])).toBe(
      "All factor names must be filled.",
    );
  });

  it("requires unique factor names, case-sensitively and after trimming", () => {
    expect(validateFactorNames(["A", " A"])).toBe(
      "Factor names must be unique.",
    );
    expect(validateFactorNames(["A", "a"])).toBeNull();
  });

  it("requires expert names but allows duplicates", () => {
    expect(validateExpertNames(["", "B"])).toBe(
      "All expert names must be filled.",
    );
    expect(validateExpertNames(["B", "B"])).toBeNull();
  });

  it("checks factors before experts, as Qt", () => {
    expect(validateNames([""], [""])).toBe("All factor names must be filled.");
    expect(validateNames(["A"], [""])).toBe("All expert names must be filled.");
  });
});
