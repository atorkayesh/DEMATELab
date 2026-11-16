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
    <div className="flex flex-wrap items-start gap-x-4 gap-y-1 py-3">
      <dt className="w-44 shrink-0 text-sm text-muted-foreground">{label}</dt>
      <dd className="min-w-0 flex-1 wrap-break-word">{children}</dd>
      <Button
        type="button"
        variant="link"
        size="sm"
        onClick={onEdit}
        aria-label={`${FLOW_TEXT.EDIT} ${label}`}
      >
        {FLOW_TEXT.EDIT}
      </Button>
    </div>
  );
}
