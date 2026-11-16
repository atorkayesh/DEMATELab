import type {
  AnalysisRequest,
  ExpertInput,
} from "@/interfaces/analysis.interface";

/** The inputs a request is built from (the store's answers). */
export interface RequestInputs {
  solver: string | null;
  threshold: string | null;
  factors: string[];
  experts: ExpertInput[];
  matrices: string[][][];
}

/** The `AnalysisRequest` for the current answers, or null while the setup is incomplete. */
export function buildAnalysisRequest(
  inputs: RequestInputs,
): AnalysisRequest | null {
  const { solver, threshold, factors, experts, matrices } = inputs;
  if (!solver || !threshold || factors.length === 0 || experts.length === 0) {
    return null;
  }
  return {
    solver_type: solver,
    threshold_method: threshold,
    factors: factors.map((name) => name.trim()),
    experts: experts.map((expert, i) => ({
      name: expert.name.trim(),
      weight: expert.weight,
      matrix: matrices[i] ?? [],
    })),
  };
}

/** Stable key of a request, for query keys and comparing against the results snapshot. */
export function requestKey(request: AnalysisRequest | null): string {
  return request ? JSON.stringify(request) : "";
}

/** Short FNV-1a hash of a string (query keys use it instead of a ~10 MB request). */
export function hashString(value: string): string {
  let hash = 0x811c9dc5;
  for (let i = 0; i < value.length; i++) {
    hash ^= value.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193);
  }
  return `${(hash >>> 0).toString(16)}-${value.length}`;
}
