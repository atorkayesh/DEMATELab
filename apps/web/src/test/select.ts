import { act, fireEvent, screen } from "@testing-library/react";

/** Opens a shadcn (Base UI) select and picks the option with the given label. */
export async function pickOption(trigger: HTMLElement, label: string) {
  if (trigger.getAttribute("aria-expanded") !== "true")
    fireEvent.click(trigger);
  const option = await screen.findByRole("option", { name: label });
  await act(async () => {
    fireEvent.pointerDown(option, { pointerType: "mouse" });
    fireEvent.mouseDown(option);
    fireEvent.pointerUp(option, { pointerType: "mouse" });
    fireEvent.mouseUp(option);
    fireEvent.click(option);
  });
}
