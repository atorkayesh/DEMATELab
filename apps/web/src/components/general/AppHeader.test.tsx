import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { AppHeader } from "@/components/general/AppHeader";

vi.mock("@tanstack/react-router", () => ({
  Link: ({ to, children }: { to: string; children: ReactNode }) => (
    <a href={to}>{children}</a>
  ),
}));

describe("AppHeader", () => {
  it("shows the logo, name and subtitle as one link home, with no navigation", () => {
    render(<AppHeader />);

    const links = screen.getAllByRole("link");
    expect(links).toHaveLength(1);
    expect(links[0].getAttribute("href")).toBe("/");
    expect(links[0].textContent).toBe("DEMATELabCause and Effect Analysis");
    expect(screen.queryByRole("navigation")).toBeNull();
  });
});
