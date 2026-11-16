import { describe, expect, it } from "vitest";
import {
  buildAnalysisRequest,
  hashString,
  requestKey,
} from "@/utils/analysis-request.utils";

describe("analysis request utils", () => {
  it("builds the request from the answers, trimming names", () => {
    expect(
      buildAnalysisRequest({
        solver: "dematel",
        threshold: "mmde",
        factors: [" A", "B "],
        experts: [{ name: " Ann ", weight: 1 }],
        matrices: [[["x"]]],
      }),
    ).toEqual({
      solver_type: "dematel",
      threshold_method: "mmde",
      factors: ["A", "B"],
      experts: [{ name: "Ann", weight: 1, matrix: [["x"]] }],
    });
  });

  it("returns null while the setup is incomplete", () => {
    const request = buildAnalysisRequest({
      solver: null,
      threshold: "mmde",
      factors: [],
      experts: [],
      matrices: [],
    });
    expect(request).toBeNull();
    expect(requestKey(request)).toBe("");
  });

  it("hashes strings stably", () => {
    expect(hashString("abc")).toBe(hashString("abc"));
    expect(hashString("abc")).not.toBe(hashString("abd"));
  });
});
