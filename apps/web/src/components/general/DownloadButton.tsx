import { DownloadIcon, LoaderCircleIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

/** An export button with a download icon, showing a spinner while its file is prepared. */
export function DownloadButton({
  label,
  pending,
  disabled,
  onClick,
}: {
  label: string;
  pending: boolean;
  disabled?: boolean;
  onClick: () => void;
}) {
  return (
    <Button
      type="button"
      variant="outline"
      onClick={onClick}
      disabled={disabled || pending}
      aria-busy={pending}
      className="w-full max-sm:h-11 sm:w-auto"
    >
      {pending ? (
        <LoaderCircleIcon className="animate-spin" data-icon="inline-start" />
      ) : (
        <DownloadIcon data-icon="inline-start" />
      )}
      {label}
    </Button>
  );
}
