import { QueryClient } from "@tanstack/react-query";

/** Query client for one router. */
export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000,
        gcTime: 30 * 60 * 1000,
      },
      // Mutations are never retried: an analysis or an AI request must not run twice.
      mutations: { retry: false },
    },
  });
}
