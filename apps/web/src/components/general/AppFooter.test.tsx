import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppFooter } from "@/components/general/AppFooter";

describe("AppFooter", () => {
  it("credits the app and links the research centre, then shows the year", () => {
    render(<AppFooter />);

    expect(screen.getByRole("contentinfo").textContent).toBe(
      `DEMATELab·Forschungszentrum Jülich·${new Date().getFullYear()}`,
    );
    const link = screen.getByRole("link");
    expect(link.getAttribute("href")).toBe("https://www.fz-juelich.de/en");
    expect(link.getAttribute("rel")).toBe("noopener noreferrer");
  });
});
