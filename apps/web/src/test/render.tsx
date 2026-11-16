import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";

/** Render inside a fresh query client (no retries); returns the client too. */
export function renderWithQuery(ui: ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return {
    queryClient,
    ...render(
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
    ),
  };
}

/**
 * jsdom has no layout: give every element a viewport size so virtualised lists render their
 * items. Returns a function that restores the original properties.
 */
export function stubLayout(width = 1000, height = 600): () => void {
  const proto = HTMLElement.prototype;
  const originals = ["clientWidth", "clientHeight"].map(
    (key) => [key, Object.getOwnPropertyDescriptor(proto, key)] as const,
  );
  Object.defineProperty(proto, "clientWidth", {
    configurable: true,
    get: () => width,
  });
  Object.defineProperty(proto, "clientHeight", {
    configurable: true,
    get: () => height,
  });
  return () => {
    for (const [key, descriptor] of originals) {
      if (descriptor) Object.defineProperty(proto, key, descriptor);
    }
  };
}
