import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ExplanationPanel } from "@/components/page-specific/analysis/ExplanationPanel";
import { explain } from "@/services/explanation.service";
import { useAnalysisStore } from "@/store/analysis.store";
import { REQUEST } from "@/test/fixtures";
import { renderWithQuery } from "@/test/render";
import { pickOption } from "@/test/select";
import { ApiError } from "@/utils/api.utils";

vi.mock("@/services/explanation.service", () => ({ explain: vi.fn() }));

const KEY = "sk-secret-key-123";

function setKey() {
  fireEvent.change(screen.getByLabelText("API Key"), {
    target: { value: KEY },
  });
}
const generate = () =>
  fireEvent.click(screen.getByRole("button", { name: "Generate Explanation" }));

describe("ExplanationPanel", () => {
  beforeEach(() => {
    vi.mocked(explain).mockReset();
    useAnalysisStore.getState().reset();
  });

  it("asks for an API key before sending anything", () => {
    renderWithQuery(<ExplanationPanel snapshot={REQUEST} />);
    generate();
    expect(screen.getByText("Please enter an API key.")).toBeDefined();
    expect(explain).not.toHaveBeenCalled();
  });

  it("prefills the engine's default model and Azure's placeholder", async () => {
    renderWithQuery(<ExplanationPanel snapshot={REQUEST} />);
    const model = screen.getByLabelText("Model") as HTMLInputElement;
    expect(model.value).toBe("gemini-2.5-pro");
    await pickOption(screen.getByLabelText("Engine"), "Azure OpenAI");
    expect(model.value).toBe("gpt-4o-mini");
    expect(model.placeholder).toBe("Enter the Azure deployment name");
  });

  it("sends the key once and never keeps it in the store or the query cache", async () => {
    vi.mocked(explain).mockResolvedValue({
      text: "Line 1\nLine 2",
      provider: "Gemini",
      model: "gemini-2.5-pro",
    });
    const { queryClient } = renderWithQuery(
      <ExplanationPanel snapshot={REQUEST} />,
    );
    setKey();
    generate();

    expect(await screen.findByText("Done")).toBeDefined();
    expect(screen.getByLabelText("Explanation").textContent).toBe(
      "Line 1\nLine 2",
    );
    expect(vi.mocked(explain).mock.calls[0][0]).toMatchObject({
      analysis: REQUEST,
      provider: "Gemini",
      api_key: KEY,
      model: "gemini-2.5-pro",
    });
    expect(JSON.stringify(useAnalysisStore.getState())).not.toContain(KEY);
    const cached = JSON.stringify([
      queryClient
        .getQueryCache()
        .getAll()
        .map((query) => [query.queryKey, query.state]),
      queryClient
        .getMutationCache()
        .getAll()
        .map((mutation) => [mutation.options.mutationKey, mutation.state]),
    ]);
    expect(cached).not.toContain(KEY);
  });

  it("shows Error and the API's message in the output on failure", async () => {
    vi.mocked(explain).mockRejectedValue(
      new ApiError("The AI provider rejected the API key.", 502),
    );
    renderWithQuery(<ExplanationPanel snapshot={REQUEST} />);
    setKey();
    generate();

    expect(await screen.findByText("Error")).toBeDefined();
    expect(screen.getByLabelText("Explanation").textContent).toBe(
      "The AI provider rejected the API key.",
    );
  });

  it("asks Azure users for the endpoint and remembers it", async () => {
    vi.mocked(explain).mockResolvedValue({
      text: "T",
      provider: "Azure OpenAI",
      model: "d",
    });
    renderWithQuery(<ExplanationPanel snapshot={REQUEST} />);
    await pickOption(screen.getByLabelText("Engine"), "Azure OpenAI");
    setKey();
    generate();

    fireEvent.click(await screen.findByRole("button", { name: "Cancel" }));
    expect(
      await screen.findByText("Azure OpenAI endpoint is required."),
    ).toBeDefined();

    generate();
    const endpoint = await screen.findByRole("textbox", {
      name: "Azure OpenAI Endpoint",
    });
    fireEvent.change(endpoint, {
      target: { value: " https://x.openai.azure.com " },
    });
    fireEvent.click(screen.getByRole("button", { name: "OK" }));
    await waitFor(() => expect(explain).toHaveBeenCalledOnce());
    expect(vi.mocked(explain).mock.calls[0][0].azure_endpoint).toBe(
      "https://x.openai.azure.com",
    );

    generate();
    expect(
      (
        (await screen.findByRole("textbox", {
          name: "Azure OpenAI Endpoint",
        })) as HTMLInputElement
      ).value,
    ).toBe("https://x.openai.azure.com");
  });
});
