import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ExplanationPanel } from "@/components/page-specific/analysis/ExplanationPanel";
import { toast } from "sonner";
import {
  explain,
  getExplanationProviders,
} from "@/services/explanation.service";
import { useAnalysisStore } from "@/store/analysis.store";
import { EXPLANATION_PROVIDERS, REQUEST } from "@/test/fixtures";
import { renderWithQuery } from "@/test/render";
import { pickOption } from "@/test/select";
import { ApiError } from "@/utils/api.utils";

vi.mock("@/services/explanation.service", () => ({
  explain: vi.fn(),
  getExplanationProviders: vi.fn(),
}));
vi.mock("sonner", () => ({ toast: { error: vi.fn() } }));

const KEY = "sk-secret-key-123";

function setKey() {
  fireEvent.change(screen.getByLabelText("API Key"), {
    target: { value: KEY },
  });
}
const generateButton = () =>
  screen.getByRole("button", { name: "Generate Explanation" });
const generate = () => fireEvent.click(generateButton());
const providerSelect = () => screen.findByLabelText("AI Provider");

async function renderPanel() {
  const result = renderWithQuery(<ExplanationPanel snapshot={REQUEST} />);
  await providerSelect();
  return result;
}

describe("ExplanationPanel", () => {
  beforeEach(() => {
    vi.mocked(explain).mockReset();
    vi.mocked(toast.error).mockReset();
    vi.mocked(getExplanationProviders).mockResolvedValue(EXPLANATION_PROVIDERS);
    useAnalysisStore.getState().reset();
  });

  it("asks for an API key before sending anything", async () => {
    await renderPanel();
    generate();
    expect(screen.getByText("Please enter an API key.")).toBeDefined();
    expect(explain).not.toHaveBeenCalled();
  });

  it("hides the API key until the eye button is pressed", async () => {
    renderWithQuery(<ExplanationPanel snapshot={REQUEST} />);
    const key = (await screen.findByLabelText("API Key")) as HTMLInputElement;
    expect(key.type).toBe("password");
    fireEvent.click(screen.getByRole("button", { name: "Show API key" }));
    expect(key.type).toBe("text");
    fireEvent.click(screen.getByRole("button", { name: "Hide API key" }));
    expect(key.type).toBe("password");
  });

  it("tells users their API key is never stored", () => {
    vi.mocked(getExplanationProviders).mockReturnValue(new Promise(() => {}));
    renderWithQuery(<ExplanationPanel snapshot={REQUEST} />);
    expect(
      screen.getByText(/never saved, stored in a database or logged/),
    ).toBeDefined();
  });

  it("lists the API's providers and resets the model to each default", async () => {
    await renderPanel();
    const model = screen.getByLabelText("Model");
    expect(model.textContent).toContain("gemini-3.5-flash-lite");
    await pickOption(model, "gemini-4-carbon");
    expect(screen.getByLabelText("Model").textContent).toContain(
      "gemini-4-carbon",
    );
    await pickOption(await providerSelect(), "Anthropic");
    expect(screen.getByLabelText("Model").textContent).toContain(
      "claude-haiku-5-5",
    );
  });

  it("gives Azure an empty deployment field and blocks Generate until filled", async () => {
    await renderPanel();
    await pickOption(await providerSelect(), "Azure OpenAI");
    const model = screen.getByLabelText("Model") as HTMLInputElement;
    expect(model.value).toBe("");
    expect(model.placeholder).toBe(
      "Your Azure deployment name, e.g. gpt-4o-mini",
    );
    setKey();
    expect((generateButton() as HTMLButtonElement).disabled).toBe(true);
    fireEvent.change(model, { target: { value: "my-dep" } });
    expect((generateButton() as HTMLButtonElement).disabled).toBe(false);
  });

  it("sends the key once and never keeps it in the store or the query cache", async () => {
    vi.mocked(explain).mockResolvedValue({
      text: "Line 1\nLine 2",
      provider: "Gemini",
      model: "gemini-3.5-flash-lite",
    });
    const { queryClient } = await renderPanel();
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
      model: "gemini-3.5-flash-lite",
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

  it("shows Error and toasts the API's message on failure", async () => {
    vi.mocked(explain).mockRejectedValue(
      new ApiError("The AI provider rejected the API key.", 502),
    );
    await renderPanel();
    setKey();
    generate();

    expect(await screen.findByText("Error")).toBeDefined();
    expect(toast.error).toHaveBeenCalledWith(
      "Could not generate the explanation",
      { description: "The AI provider rejected the API key." },
    );
    expect(screen.getByLabelText("Explanation").textContent).toBe("");
  });

  it("asks Azure users for the endpoint and remembers it", async () => {
    vi.mocked(explain).mockResolvedValue({
      text: "T",
      provider: "Azure OpenAI",
      model: "d",
    });
    await renderPanel();
    await pickOption(await providerSelect(), "Azure OpenAI");
    fireEvent.change(screen.getByLabelText("Model"), {
      target: { value: "d" },
    });
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
