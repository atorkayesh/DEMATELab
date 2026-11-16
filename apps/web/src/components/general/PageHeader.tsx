import type { ReactNode } from "react";

/** Shared top spacing for pages with a text heading and optional description. */
export function PageHeader({ children }: { children: ReactNode }) {
  return <div className="pt-16 flex flex-col gap-1">{children}</div>;
}
