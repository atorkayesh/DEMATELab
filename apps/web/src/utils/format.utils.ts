import type { ResultValue } from "@/interfaces/result.interface";

/** Fixed decimals, e.g. `formatFixed(0.12345, 4)` → `0.1235`. */
export function formatFixed(value: number, decimals: number): string {
  return value.toFixed(decimals);
}

/** A sign before positive values too, e.g. `+0.25` (zero shows `+0.00`, as in Qt). */
export function formatSigned(value: number, decimals: number): string {
  return value >= 0 ? `+${value.toFixed(decimals)}` : value.toFixed(decimals);
}

/** A result cell as in Qt: crisp `0.1234`, fuzzy `(l, m, u)` or grey `(lo, hi)`, 4 decimals. */
export function formatResultValue(value: ResultValue): string {
  if (Array.isArray(value)) {
    return `(${value.map((part) => part.toFixed(4)).join(", ")})`;
  }
  return value.toFixed(4);
}

/** Threshold value with 4 decimals, or an em dash when there is none. */
export function formatThreshold(value: number | null | undefined): string {
  return value == null ? "—" : value.toFixed(4);
}

/** A weight with the API's number of decimals. */
export function formatWeight(value: number, decimals: number): string {
  return value.toFixed(decimals);
}
