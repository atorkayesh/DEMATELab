import { afterEach, describe, expect, it, vi } from "vitest";
import { runAnalysis } from "@/services/analysis.service";
import { getChart } from "@/services/charts.service";
import { exportXlsx } from "@/services/export.service";
import { getScales } from "@/services/scales.service";
import {
  getDefaultWeights,
  normalizeWeights,
} from "@/services/weights.service";
import {
  ANALYSIS_DATA,
  apiErrorBody,
  apiJson,
  REQUEST,
  SCALES,
} from "@/test/fixtures";

const BASE = "http://localhost:50001/api/v1";

function stubFetch(response: Response) {
  const fetchMock = vi.fn().mockResolvedValue(response);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("analysis services", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("loads and validates the scales", async () => {
    const fetchMock = stubFetch(apiJson(SCALES));
    await expect(getScales()).resolves.toEqual(SCALES);
    expect(fetchMock.mock.calls[0][0]).toBe(`${BASE}/scales`);
  });

  it("rejects scales that do not match the schema", async () => {
    stubFetch(apiJson({ standard: {} }));
    await expect(getScales()).rejects.toThrow();
  });

  it("posts the expert count for default weights", async () => {
    const fetchMock = stubFetch(apiJson({ weights: [0.5, 0.5] }));
    await expect(getDefaultWeights(2)).resolves.toEqual([0.5, 0.5]);
    expect(fetchMock.mock.calls[0][0]).toBe(`${BASE}/weights/defaults`);
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({
      expert_count: 2,
    });
  });

  it("returns corrected weights, or the API's weight message", async () => {
    stubFetch(apiJson({ weights: [0.6, 0.4] }));
    await expect(normalizeWeights([0.601, 0.4])).resolves.toEqual([0.6, 0.4]);
    stubFetch(apiJson(apiErrorBody("Expert weights must sum to 1."), 422));
    await expect(normalizeWeights([0.2])).rejects.toThrow(
      "Expert weights must sum to 1.",
    );
  });

  it("runs the analysis and validates the discriminated result", async () => {
    const fetchMock = stubFetch(apiJson(ANALYSIS_DATA));
    await expect(runAnalysis(REQUEST)).resolves.toEqual(ANALYSIS_DATA);
    expect(fetchMock.mock.calls[0][0]).toBe(`${BASE}/analysis`);
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual(REQUEST);
  });

  it("rejects a result whose fields do not match its solver type", async () => {
    stubFetch(
      apiJson({
        ...ANALYSIS_DATA,
        result: { ...ANALYSIS_DATA.result, solver_type: "grey_dematel" },
      }),
    );
    await expect(runAnalysis(REQUEST)).rejects.toThrow();
  });

  it("downloads the XLSX and charts as blobs with the right query", async () => {
    const fetchMock = stubFetch(new Response("xlsx"));
    expect(await (await exportXlsx(REQUEST)).text()).toBe("xlsx");
    expect(fetchMock.mock.calls[0][0]).toBe(`${BASE}/analysis/export/xlsx`);

    stubFetch(new Response("png"));
    await getChart(REQUEST, "causal-diagram", "standard", 100);
    expect(vi.mocked(fetch).mock.calls[0][0]).toBe(
      `${BASE}/analysis/charts/causal-diagram?dpi=100`,
    );
    stubFetch(new Response("png"));
    await getChart(REQUEST, "heatmap", "cluster", 300);
    expect(vi.mocked(fetch).mock.calls[0][0]).toBe(
      `${BASE}/analysis/charts/heatmap?mode=cluster&dpi=300`,
    );
  });

  it("rejects a failed cluster heatmap with the API's message", async () => {
    stubFetch(
      apiJson(
        apiErrorBody("Could not generate cluster heatmap: too few values"),
        422,
      ),
    );
    await expect(getChart(REQUEST, "heatmap", "cluster", 100)).rejects.toThrow(
      "Could not generate cluster heatmap: too few values",
    );
  });
});
