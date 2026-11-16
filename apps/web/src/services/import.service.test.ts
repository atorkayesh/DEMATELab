import { afterEach, describe, expect, it, vi } from "vitest";
import { explain } from "@/services/explanation.service";
import { importMatrix, importWorkbook } from "@/services/import.service";
import { apiErrorBody, apiJson, REQUEST } from "@/test/fixtures";

const file = new File(["x"], "matrix.xlsx");

describe("import and explanation services", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("uploads one matrix as multipart with the factor count", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(apiJson({ factor_names: null, matrix: [["a"]] }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(importMatrix(file, 4)).resolves.toEqual({
      factor_names: null,
      matrix: [["a"]],
    });
    const body = fetchMock.mock.calls[0][1].body as FormData;
    expect(body.get("file")).toBeInstanceOf(File);
    expect(body.get("factor_count")).toBe("4");
  });

  it("uploads a workbook with every expert name", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      apiJson({
        factor_names: ["A", "B"],
        matrices: [{ expert_name: "Ann", matrix: [["a"]] }],
        matched_by: "name",
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const data = await importWorkbook(file, 2, ["Ann", "Bo"]);

    expect(data.matched_by).toBe("name");
    const body = fetchMock.mock.calls[0][1].body as FormData;
    expect(body.getAll("expert_names")).toEqual(["Ann", "Bo"]);
  });

  it("rejects an import with the parser's message", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          apiJson(apiErrorBody("Imported matrix must be exactly 4 x 4."), 422),
        ),
    );
    await expect(importMatrix(file, 4)).rejects.toThrow(
      "Imported matrix must be exactly 4 x 4.",
    );
  });

  it("sends the explanation request once and returns the text", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(apiJson({ text: "T", provider: "Groq", model: "m" }));
    vi.stubGlobal("fetch", fetchMock);

    const data = await explain({
      analysis: REQUEST,
      provider: "Groq",
      api_key: "k",
    });

    expect(data.text).toBe("T");
    expect(JSON.parse(fetchMock.mock.calls[0][1].body).api_key).toBe("k");
  });
});
