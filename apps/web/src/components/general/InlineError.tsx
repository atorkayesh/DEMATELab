import { cn } from "@/lib/utils";

/** A validation or request error shown next to the control it belongs to (Qt used dialogs). */
export function InlineError({
  message,
  className,
}: {
  message: string | null | undefined;
  className?: string;
}) {
  if (!message) return null;
  return (
    <p
      role="alert"
      className={cn(
        "text-sm whitespace-pre-line text-destructive wrap-break-word",
        className,
      )}
    >
      {message}
    </p>
  );
}
