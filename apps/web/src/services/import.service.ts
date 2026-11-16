import { API_ENDPOINTS } from "@/constants/api.constants";
import {
  type MatrixImportData,
  matrixImportResponseSchema,
  type WorkbookImportData,
  workbookImportResponseSchema,
} from "@/interfaces/import.interface";
import { apiData } from "@/utils/api.utils";

/** One matrix from the first sheet of an `.xlsx` file. */
export function importMatrix(
  file: File,
  factorCount: number,
): Promise<MatrixImportData> {
  const form = new FormData();
  form.append("file", file);
  form.append("factor_count", String(factorCount));
  return apiData(
    API_ENDPOINTS.IMPORT_MATRIX,
    { method: "POST", body: form },
    matrixImportResponseSchema,
  );
}

/** One matrix per expert from an `.xlsx` workbook, in the order of `expertNames`. */
export function importWorkbook(
  file: File,
  factorCount: number,
  expertNames: string[],
): Promise<WorkbookImportData> {
  const form = new FormData();
  form.append("file", file);
  form.append("factor_count", String(factorCount));
  for (const name of expertNames) form.append("expert_names", name);
  return apiData(
    API_ENDPOINTS.IMPORT_WORKBOOK,
    { method: "POST", body: form },
    workbookImportResponseSchema,
  );
}
