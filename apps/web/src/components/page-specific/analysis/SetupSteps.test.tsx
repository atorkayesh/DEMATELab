import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ExpertCountStep } from "@/components/page-specific/analysis/ExpertCountStep";
import { ExpertWeightsStep } from "@/components/page-specific/analysis/ExpertWeightsStep";
import { FactorCountStep } from "@/components/page-specific/analysis/FactorCountStep";
import { FactorNamesStep } from "@/components/page-specific/analysis/FactorNamesStep";
import { SolverStep } from "@/components/page-specific/analysis/SolverStep";
import {
  getDefaultWeights,
  normalizeWeights,
} from "@/services/weights.service";
import { useAnalysisStore } from "@/store/analysis.store";
import { SCALES, STANDARD_SCALE } from "@/test/fixtures";
import { renderWithQuery } from "@/test/render";
import { ApiError } from "@/utils/api.utils";

vi.mock("@/services/weights.service", () => ({
  getDefaultWeights: vi.fn(),
  normalizeWeights: vi.fn(),
}));

const store = () => useAnalysisStore.getState();
const nav = () => ({ number: 1, onAdvance: vi.fn(), onBack: vi.fn() });

function answerSetup() {
  store().setSolver("dematel", STANDARD_SCALE);
  store().setExpertCount(2, [0.5, 0.5]);
  store().setFactorCount(3);
}

describe("setup steps", () => {
  beforeEach(() => {
    store().reset();
    vi.mocked(normalizeWeights).mockReset();
    vi.mocked(getDefaultWeights).mockReset();
  });

  it("clamps a typed count on Enter and continues with it", () => {
    answerSetup();
    const props = nav();
    renderWithQuery(<FactorCountStep scales={SCALES} {...props} />);
    const input = screen.getByRole("textbox", { name: "Number of factors" });

    fireEvent.change(input, { target: { value: "200" } });
    fireEvent.keyDown(input, { key: "Enter" });

    expect(store().factorCount).toBe(100);
    expect(props.onAdvance).toHaveBeenCalledOnce();
  });

  it("clamps a typed weight on Enter before checking the weights", async () => {
    answerSetup();
    vi.mocked(normalizeWeights).mockResolvedValue([0.667, 0.333]);
    const props = nav();
    renderWithQuery(<ExpertWeightsStep scales={SCALES} {...props} />);
    const input = screen.getByRole("textbox", { name: "Expert 1 weight" });

    fireEvent.change(input, { target: { value: "1.5" } });
    fireEvent.keyDown(input, { key: "Enter" });

    await waitFor(() => expect(props.onAdvance).toHaveBeenCalledOnce());
    expect(vi.mocked(normalizeWeights).mock.calls[0][0]).toEqual([1, 0.5]);
  });

  it("asks before fewer experts drop an edited matrix, then applies the count", async () => {
    answerSetup();
    store().setCell(1, 0, 1, "High influence");
    vi.mocked(getDefaultWeights).mockResolvedValue([1]);
    const props = nav();
    renderWithQuery(<ExpertCountStep scales={SCALES} {...props} />);

    fireEvent.change(
      screen.getByRole("textbox", { name: "Number of experts" }),
      { target: { value: "1" } },
    );
    fireEvent.click(screen.getByRole("button", { name: "OK" }));
    expect(
      await screen.findByText(
        "The removed experts have matrix values that will be lost. Continue?",
      ),
    ).toBeDefined();
    expect(getDefaultWeights).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() => expect(props.onAdvance).toHaveBeenCalledOnce());
    expect(store().expertCount).toBe(1);
    expect(store().matrices).toHaveLength(1);
  });

  it("warns before switching solver family; Cancel restores the previous solver", async () => {
    answerSetup();
    store().setCell(0, 0, 1, "High influence");
    const props = nav();
    renderWithQuery(<SolverStep scales={SCALES} {...props} />);

    fireEvent.click(screen.getByRole("radio", { name: /Fuzzy Z-DEMATEL/ }));
    fireEvent.click(screen.getByRole("button", { name: "OK" }));
    expect(await screen.findByText("Solver Change Detected")).toBeDefined();
    expect(
      screen.getByText(
        /Fuzzy Z-DEMATEL requires combined influence–reliability/,
      ),
    ).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    await waitFor(() =>
      expect(
        (screen.getByRole("radio", { name: "DEMATEL" }) as HTMLInputElement)
          .checked,
      ).toBe(true),
    );
    expect(store().solver).toBe("dematel");
    expect(store().matrices[0][0][1]).toBe("High influence");
    expect(props.onAdvance).not.toHaveBeenCalled();
  });

  it("resets the matrices when the family change is confirmed", async () => {
    answerSetup();
    store().setCell(0, 0, 1, "High influence");
    const props = nav();
    renderWithQuery(<SolverStep scales={SCALES} {...props} />);

    fireEvent.click(screen.getByRole("radio", { name: /Fuzzy Z-DEMATEL/ }));
    fireEvent.click(screen.getByRole("button", { name: "OK" }));
    fireEvent.click(await screen.findByRole("button", { name: "OK" }));

    await waitFor(() => expect(store().solver).toBe("fuzzy_z_dematel"));
    expect(store().matrices[0][0][1]).toBe("No influence with VH reliability");
    expect(props.onAdvance).toHaveBeenCalled();
  });

  it("asks before fewer factors drop edited cells", async () => {
    answerSetup();
    store().setCell(0, 0, 2, "High influence");
    const props = nav();
    renderWithQuery(<FactorCountStep scales={SCALES} {...props} />);

    fireEvent.change(
      screen.getByRole("textbox", { name: "Number of factors" }),
      {
        target: { value: "2" },
      },
    );
    fireEvent.click(screen.getByRole("button", { name: "OK" }));
    expect(
      await screen.findByText(
        "The removed factors have matrix values that will be lost. Continue?",
      ),
    ).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    await waitFor(() => expect(store().factorCount).toBe(3));
    expect(props.onAdvance).not.toHaveBeenCalled();
  });

  it("checks factor names with Qt's messages", () => {
    answerSetup();
    const props = nav();
    renderWithQuery(<FactorNamesStep {...props} />);

    fireEvent.change(screen.getByRole("textbox", { name: "Factor 2 name" }), {
      target: { value: "F1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "OK" }));
    expect(screen.getByRole("alert").textContent).toBe(
      "Factor names must be unique.",
    );
    fireEvent.change(screen.getByRole("textbox", { name: "Factor 2 name" }), {
      target: { value: "Cost" },
    });
    fireEvent.click(screen.getByRole("button", { name: "OK" }));
    expect(props.onAdvance).toHaveBeenCalledOnce();
    expect(store().factors[1]).toBe("Cost");
  });

  it("requires expert names, then writes the API's corrected weights back", async () => {
    answerSetup();
    vi.mocked(normalizeWeights).mockResolvedValue([0.6, 0.4]);
    const props = nav();
    renderWithQuery(<ExpertWeightsStep scales={SCALES} {...props} />);

    fireEvent.change(screen.getByRole("textbox", { name: "Expert 1 name" }), {
      target: { value: " " },
    });
    fireEvent.click(screen.getByRole("button", { name: "OK" }));
    expect(screen.getByRole("alert").textContent).toBe(
      "All expert names must be filled.",
    );
    fireEvent.change(screen.getByRole("textbox", { name: "Expert 1 name" }), {
      target: { value: "Ann" },
    });
    fireEvent.change(screen.getByRole("textbox", { name: "Expert 1 weight" }), {
      target: { value: "0.601" },
    });
    fireEvent.click(screen.getByRole("button", { name: "OK" }));

    await waitFor(() => expect(props.onAdvance).toHaveBeenCalledOnce());
    expect(vi.mocked(normalizeWeights).mock.calls[0][0]).toEqual([0.601, 0.5]);
    expect(store().experts.map((expert) => expert.weight)).toEqual([0.6, 0.4]);
    expect(
      (
        screen.getByRole("textbox", {
          name: "Expert 1 weight",
        }) as HTMLInputElement
      ).value,
    ).toBe("0.600");
  });

  it("shows the API's weight error inline and the reset note", async () => {
    answerSetup();
    store().setExpertCount(3, [0.334, 0.333, 0.333]);
    vi.mocked(normalizeWeights).mockRejectedValue(
      new ApiError("Expert weights must sum to 1.", 422),
    );
    const props = nav();
    renderWithQuery(<ExpertWeightsStep scales={SCALES} {...props} />);

    expect(
      screen.getByText(/the weights were reset to equal defaults/),
    ).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: "OK" }));
    expect((await screen.findByRole("alert")).textContent).toBe(
      "Expert weights must sum to 1.",
    );
    expect(props.onAdvance).not.toHaveBeenCalled();
  });
});
