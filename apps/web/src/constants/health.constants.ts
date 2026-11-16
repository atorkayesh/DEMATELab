import type { RowState } from "@/interfaces/health.interface";

export const HEALTH_QUERY_KEY = ["health"] as const;

export const HEALTH_REFETCH_INTERVAL_MS = 30_000;

/** Key of the API's own entry in the health `services`. */
export const HEALTH_API_SERVICE_KEY = "api";

/** The API itself: the only row (it has no dependencies); outage when the request fails. */
export const HEALTH_API_ROW = {
  label: "API",
  description: "Analysis, charts, exports and AI explanations",
} as const;

/** Label on the right of a row and the colour of its dot. */
export const ROW_STATE_DISPLAY: Record<
  RowState,
  { label: string; dotClass: string }
> = {
  operational: { label: "Operational", dotClass: "bg-green-500" },
  outage: { label: "Outage", dotClass: "bg-red-500" },
  checking: { label: "Checking…", dotClass: "animate-pulse bg-line-strong" },
};

/** Summary under the card title for the overall state. */
export const HEALTH_SUMMARY: Record<RowState, string> = {
  operational: "All systems operational",
  outage: "Outage",
  checking: "Checking…",
};

export const HEALTH_MESSAGES = {
  TITLE: "System status",
  API_UNREACHABLE: "The API is unreachable",
  LAST_CHECKED: "Last checked",
} as const;
