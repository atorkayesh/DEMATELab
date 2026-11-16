import { API_ENDPOINTS } from "@/constants/api.constants";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import { apiBlob, jsonPost } from "@/utils/api.utils";

/** The results workbook (`dematel_results.xlsx`). */
export function exportXlsx(request: AnalysisRequest): Promise<Blob> {
  return apiBlob(API_ENDPOINTS.EXPORT_XLSX, jsonPost(request));
}
