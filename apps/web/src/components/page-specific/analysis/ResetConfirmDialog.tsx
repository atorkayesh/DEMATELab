import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { RESET_CONFIRM_TEXT } from "@/constants/analysis.constants";

/** Asks before an answer change discards data (edited matrix cells); Cancel keeps everything. */
export function ResetConfirmDialog({
  open,
  title = RESET_CONFIRM_TEXT.TITLE,
  paragraphs,
  confirmLabel = RESET_CONFIRM_TEXT.CONFIRM,
  cancelLabel = RESET_CONFIRM_TEXT.CANCEL,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title?: string;
  paragraphs: readonly string[];
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <AlertDialog
      open={open}
      onOpenChange={(next) => {
        if (!next) onCancel();
      }}
    >
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription
            render={<div />}
            className="flex flex-col gap-2"
          >
            {paragraphs.map((text) => (
              <p key={text}>{text}</p>
            ))}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{cancelLabel}</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm}>
            {confirmLabel}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
