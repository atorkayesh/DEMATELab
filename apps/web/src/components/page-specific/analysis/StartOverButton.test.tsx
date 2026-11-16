import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { StartOverButton } from "@/components/page-specific/analysis/StartOverButton";
import { useAnalysisStore } from "@/store/analysis.store";

const navigate = vi.hoisted(() => vi.fn());
vi.mock("@tanstack/react-router", () => ({ useNavigate: () => navigate }));

const store = () => useAnalysisStore.getState();

describe("StartOverButton", () => {
  beforeEach(() => {
    store().reset();
    navigate.mockReset();
  });

  it("is hidden while nothing has been answered", () => {
    render(<StartOverButton />);
    expect(screen.queryByRole("button", { name: "Start over" })).toBeNull();
  });

  it("keeps everything when the dialog is cancelled", () => {
    useAnalysisStore.setState({ answered: ["solver", "threshold"] });
    render(<StartOverButton />);
    fireEvent.click(screen.getByRole("button", { name: "Start over" }));
    expect(
      screen.getByText("All answers, matrices and results will be cleared."),
    ).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(store().answered).toEqual(["solver", "threshold"]);
    expect(navigate).not.toHaveBeenCalled();
  });

  it("clears every answer and opens the first step after confirmation", () => {
    useAnalysisStore.setState({ answered: ["solver"], factorCount: 5 });
    render(<StartOverButton />);
    fireEvent.click(screen.getByRole("button", { name: "Start over" }));
    const confirm = screen
      .getAllByRole("button", { name: "Start over" })
      .find((button) => button.closest("[role=alertdialog]"));
    fireEvent.click(confirm as HTMLElement);
    expect(store().answered).toEqual([]);
    expect(store().factorCount).toBeNull();
    expect(navigate).toHaveBeenCalledWith({ search: { step: "solver" } });
  });
});
