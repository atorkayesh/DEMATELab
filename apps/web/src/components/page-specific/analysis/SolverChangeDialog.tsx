import { ResetConfirmDialog } from "@/components/page-specific/analysis/ResetConfirmDialog";
import { SOLVER_CHANGE_TEXT } from "@/constants/analysis.constants";

/** Qt's "Solver Change Detected" warning when switching between standard and Z solvers. */
export function SolverChangeDialog({
  open,
  toZ,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  toZ: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <ResetConfirmDialog
      open={open}
      title={SOLVER_CHANGE_TEXT.TITLE}
      paragraphs={
        toZ ? SOLVER_CHANGE_TEXT.TO_Z : SOLVER_CHANGE_TEXT.TO_STANDARD
      }
      confirmLabel={SOLVER_CHANGE_TEXT.CONFIRM}
      cancelLabel={SOLVER_CHANGE_TEXT.CANCEL}
      onConfirm={onConfirm}
      onCancel={onCancel}
    />
  );
}
