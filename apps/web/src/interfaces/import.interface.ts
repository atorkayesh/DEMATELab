import { z } from "zod";
import { apiResponseSchema } from "@/interfaces/api.interface";

export const matrixImportDataSchema = z.object({
  factor_names: z.array(z.string()).nullish(),
  matrix: z.array(z.array(z.string())),
});

export const workbookImportDataSchema = z.object({
  factor_names: z.array(z.string()).nullish(),
  matrices: z.array(
    z.object({ expert_name: z.string(), matrix: z.array(z.array(z.string())) }),
  ),
  matched_by: z.enum(["name", "order"]),
});

export const matrixImportResponseSchema = apiResponseSchema(
  matrixImportDataSchema,
);
export const workbookImportResponseSchema = apiResponseSchema(
  workbookImportDataSchema,
);

export type MatrixImportData = z.infer<typeof matrixImportDataSchema>;
export type WorkbookImportData = z.infer<typeof workbookImportDataSchema>;
