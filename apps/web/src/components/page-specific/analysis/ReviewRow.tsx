import type { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { FLOW_TEXT } from "@/constants/analysis.constants";

/** One answer on the Review step, with an Edit link to its question. */
export function ReviewRow({
  label,
  children,
  onEdit,
}: {
  label: string;
  children: ReactNode;
  onEdit: () => void;
}) {
  return (
    <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-x-4 gap-y-1 py-3 sm:grid-cols-[11rem_minmax(0,1fr)_auto]">
      <dt className="text-sm text-muted-foreground sm:col-start-1 sm:row-start-1">
        {label}
      </dt>
      <dd className="col-span-2 row-start-2 min-w-0 wrap-break-word sm:col-span-1 sm:col-start-2 sm:row-start-1">
        {children}
      </dd>
      <Button
        type="button"
        variant="link"
        size="sm"
        onClick={onEdit}
        aria-label={`${FLOW_TEXT.EDIT} ${label}`}
        className="col-start-2 row-start-1 sm:col-start-3"
      >
        {FLOW_TEXT.EDIT}
      </Button>
    </div>
  );
}
