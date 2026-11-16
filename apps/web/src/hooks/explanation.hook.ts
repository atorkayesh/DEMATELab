import { useMutation } from "@tanstack/react-query";
import { useRef } from "react";
import { MUTATION_KEYS } from "@/constants/query.constants";
import type {
  ExplanationData,
  ExplanationRequest,
} from "@/interfaces/explanation.interface";
import { explain } from "@/services/explanation.service";

/**
 * Generate an AI explanation.
 *
 * The request (with the API key) is handed over through a ref and cleared at once, never as the
 * mutation's variables, so the key is not kept in the mutation cache.
 */
export function useExplanation() {
  const pending = useRef<ExplanationRequest | null>(null);
  const mutation = useMutation({
    mutationKey: MUTATION_KEYS.EXPLANATION,
    gcTime: 0,
    mutationFn: () => {
      const request = pending.current;
      pending.current = null;
      if (!request) throw new Error("No explanation request");
      return explain(request);
    },
  });
  const generate = (
    request: ExplanationRequest,
    callbacks: {
      onSuccess: (data: ExplanationData) => void;
      onError: (error: Error) => void;
    },
  ) => {
    pending.current = request;
    mutation.mutate(undefined, callbacks);
  };
  return { ...mutation, generate };
}
