import { useMutation } from "@tanstack/react-query";
import { MUTATION_KEYS } from "@/constants/query.constants";
import { importMatrix, importWorkbook } from "@/services/import.service";
import { useAnalysisStore } from "@/store/analysis.store";

/** Import one expert's matrix; imported factor names rename the factors everywhere. */
export function useImportMatrix(expert: number) {
  const renameFactors = useAnalysisStore((state) => state.renameFactors);
  const applyImportedMatrix = useAnalysisStore(
    (state) => state.applyImportedMatrix,
  );
  return useMutation({
    mutationKey: MUTATION_KEYS.IMPORT_MATRIX,
    mutationFn: ({ file, factorCount }: { file: File; factorCount: number }) =>
      importMatrix(file, factorCount),
    onSuccess: (data) => {
      if (data.factor_names) renameFactors(data.factor_names);
      applyImportedMatrix(expert, data.matrix);
    },
  });
}

/** Import every expert's matrix from one workbook (one sheet per expert). */
export function useImportWorkbook() {
  const renameFactors = useAnalysisStore((state) => state.renameFactors);
  const applyImportedWorkbook = useAnalysisStore(
    (state) => state.applyImportedWorkbook,
  );
  return useMutation({
    mutationKey: MUTATION_KEYS.IMPORT_WORKBOOK,
    mutationFn: ({
      file,
      factorCount,
      expertNames,
    }: {
      file: File;
      factorCount: number;
      expertNames: string[];
    }) => importWorkbook(file, factorCount, expertNames),
    onSuccess: (data) => {
      if (data.factor_names) renameFactors(data.factor_names);
      applyImportedWorkbook(data.matrices.map((entry) => entry.matrix));
    },
  });
}
