import { UploadIcon } from "lucide-react";
import { type ChangeEvent, useRef, useState } from "react";
import { InlineError } from "@/components/general/InlineError";
import { Button } from "@/components/ui/button";
import { IMPORT_TEXT } from "@/constants/analysis.constants";
import { useImportMatrix, useImportWorkbook } from "@/hooks/import.hook";
import { useAnalysisStore } from "@/store/analysis.store";
import { errorMessage } from "@/utils/api.utils";

/** The file chosen in an `<input type="file">`, and the input reset so the same file can be re-picked. */
function takeFile(event: ChangeEvent<HTMLInputElement>): File | null {
  const file = event.target.files?.[0] ?? null;
  event.target.value = "";
  return file;
}

/**
 * Qt's import buttons: this expert's matrix, and (on the first matrix step) every expert's matrix
 * from one workbook. The Z scale has no import: its button explains why, and import-all is hidden.
 */
export function MatrixImportActions({
  expert,
  showImportAll,
  isZ,
}: {
  expert: number;
  showImportAll: boolean;
  isZ: boolean;
}) {
  const matrixInput = useRef<HTMLInputElement>(null);
  const workbookInput = useRef<HTMLInputElement>(null);
  const [notAvailable, setNotAvailable] = useState(false);
  const importMatrix = useImportMatrix(expert);
  const importWorkbook = useImportWorkbook();
  const pending = importMatrix.isPending || importWorkbook.isPending;
  const error = importMatrix.error ?? importWorkbook.error;

  const onMatrixFile = (event: ChangeEvent<HTMLInputElement>) => {
    const file = takeFile(event);
    if (!file) return;
    importWorkbook.reset();
    const { factorCount } = useAnalysisStore.getState();
    importMatrix.mutate({ file, factorCount: factorCount ?? 0 });
  };
  const onWorkbookFile = (event: ChangeEvent<HTMLInputElement>) => {
    const file = takeFile(event);
    if (!file) return;
    importMatrix.reset();
    const { factorCount, experts } = useAnalysisStore.getState();
    importWorkbook.mutate({
      file,
      factorCount: factorCount ?? 0,
      expertNames: experts.map((entry) => entry.name),
    });
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap justify-end gap-2">
        <Button
          type="button"
          variant="outline"
          disabled={pending}
          onClick={() =>
            isZ ? setNotAvailable(true) : matrixInput.current?.click()
          }
        >
          <UploadIcon data-icon="inline-start" />
          {IMPORT_TEXT.MATRIX}
        </Button>
        {showImportAll && !isZ && (
          <Button
            type="button"
            variant="outline"
            disabled={pending}
            onClick={() => workbookInput.current?.click()}
          >
            <UploadIcon data-icon="inline-start" />
            {IMPORT_TEXT.ALL}
          </Button>
        )}
        <input
          ref={matrixInput}
          type="file"
          accept={IMPORT_TEXT.ACCEPT}
          hidden
          data-testid="matrix-file"
          onChange={onMatrixFile}
        />
        <input
          ref={workbookInput}
          type="file"
          accept={IMPORT_TEXT.ACCEPT}
          hidden
          data-testid="workbook-file"
          onChange={onWorkbookFile}
        />
      </div>
      {isZ && notAvailable && (
        <output className="block rounded-lg bg-muted px-3 py-2 text-sm">
          <p className="font-semibold">{IMPORT_TEXT.NOT_AVAILABLE_TITLE}</p>
          <p className="whitespace-pre-line text-muted-foreground">
            {IMPORT_TEXT.NOT_AVAILABLE}
          </p>
        </output>
      )}
      <InlineError
        message={error ? IMPORT_TEXT.FAILED(errorMessage(error)) : null}
        className="text-right"
      />
    </div>
  );
}
