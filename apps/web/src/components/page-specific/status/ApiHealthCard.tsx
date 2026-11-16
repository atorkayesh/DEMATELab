import { StatusRow } from "@/components/page-specific/status/StatusRow";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  HEALTH_API_ROW,
  HEALTH_API_SERVICE_KEY,
  HEALTH_MESSAGES,
  HEALTH_SUMMARY,
} from "@/constants/health.constants";
import { useApiHealth } from "@/hooks/health.hook";
import type { RowState } from "@/interfaces/health.interface";

/**
 * System status: the API as one row (it has no dependencies) with a green or red dot, and the
 * time of the last check.
 */
export function ApiHealthCard() {
  const { data, isPending, isError, dataUpdatedAt, errorUpdatedAt } =
    useApiHealth();

  const apiUp =
    data?.status === "healthy" &&
    data.services[HEALTH_API_SERVICE_KEY]?.status !== "down";
  const state: RowState = isPending
    ? "checking"
    : isError || !apiUp
      ? "outage"
      : "operational";
  const lastCheck = Math.max(dataUpdatedAt, errorUpdatedAt);
  const checkedAt =
    lastCheck > 0 ? new Date(lastCheck).toLocaleTimeString() : null;

  return (
    <Card className="gap-0 py-0">
      <CardHeader className="border-b py-4">
        <CardTitle className="text-lg">{HEALTH_MESSAGES.TITLE}</CardTitle>
        <CardDescription>
          {HEALTH_SUMMARY[state]}
          {checkedAt && ` · ${HEALTH_MESSAGES.LAST_CHECKED} ${checkedAt}`}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <StatusRow
          label={HEALTH_API_ROW.label}
          description={
            isError
              ? HEALTH_MESSAGES.API_UNREACHABLE
              : HEALTH_API_ROW.description
          }
          state={state}
        />
      </CardContent>
    </Card>
  );
}
