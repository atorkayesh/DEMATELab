import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NumberStepper } from "@/components/general/NumberStepper";

function renderStepper(value = 4) {
  const onChange = vi.fn();
  render(
    <NumberStepper
      id="n"
      label="Number of factors"
      value={value}
      min={2}
      max={100}
      onChange={onChange}
    />,
  );
  return { onChange, input: screen.getByRole("textbox") as HTMLInputElement };
}

describe("NumberStepper", () => {
  it("clamps on blur and resets non-integers to the minimum", () => {
    const { onChange, input } = renderStepper();
    fireEvent.change(input, { target: { value: "500" } });
    fireEvent.blur(input);
    expect(onChange).toHaveBeenLastCalledWith(100);
    expect(input.value).toBe("100");
    fireEvent.change(input, { target: { value: "3.5" } });
    fireEvent.blur(input);
    expect(onChange).toHaveBeenLastCalledWith(2);
  });

  it("clamps and commits on Enter", () => {
    const { onChange, input } = renderStepper();
    fireEvent.change(input, { target: { value: "200" } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onChange).toHaveBeenLastCalledWith(100);
    expect(input.value).toBe("100");
  });

  it("steps with the buttons and arrow keys", () => {
    const { onChange, input } = renderStepper();
    fireEvent.click(
      screen.getByRole("button", { name: "Increase Number of factors" }),
    );
    expect(onChange).toHaveBeenLastCalledWith(5);
    fireEvent.keyDown(input, { key: "ArrowDown" });
    expect(onChange).toHaveBeenLastCalledWith(3);
  });
});
