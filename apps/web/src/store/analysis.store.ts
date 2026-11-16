import { create } from "zustand";
import {
  expertDefaultName,
  factorDefaultName,
} from "@/constants/analysis.constants";
import type {
  AnalysisRequest,
  ExpertInput,
  StepId,
} from "@/interfaces/analysis.interface";
import type { AnalysisData } from "@/interfaces/result.interface";
import type { MatrixScale } from "@/interfaces/scales.interface";
import { hashString, requestKey } from "@/utils/analysis-request.utils";
import { matrixStepIndex } from "@/utils/flow.utils";
import {
  createMatrix,
  resizeMatrix,
  resizeNames,
  withDiagonal,
} from "@/utils/matrix.utils";

/**
 * The analysis inputs (one answer per flow step), and the results with the request snapshot they
 * were computed from. Results, charts, exports and the AI explanation always use the snapshot.
 * Nothing is persisted, as in Qt.
 */
export interface AnalysisState {
  solver: string | null;
  threshold: string | null;
  expertCount: number | null;
  factorCount: number | null;
  /** Scale of the current solver's family; decides default and diagonal cells. */
  scale: MatrixScale | null;
  factors: string[];
  experts: ExpertInput[];
  /** One `n x n` matrix per expert; empty until solver, experts and factors are answered. */
  matrices: string[][][];
  answered: StepId[];
  /** The expert count changed and the weights were reset to the defaults. */
  weightsReset: boolean;
  snapshot: AnalysisRequest | null;
  snapshotHash: string;
  results: AnalysisData | null;
}

export interface AnalysisActions {
  /** Change the solver; a different family resets every matrix to the new defaults. */
  setSolver: (solver: string, scale: MatrixScale) => void;
  setThreshold: (threshold: string) => void;
  /** Resize the experts, keeping names and matrices of the remaining ones; weights replaced. */
  setExpertCount: (count: number, weights: number[]) => void;
  /** Resize the factors, keeping names and cells of the remaining ones. */
  setFactorCount: (count: number) => void;
  setFactorName: (index: number, name: string) => void;
  setExpertName: (index: number, name: string) => void;
  setExpertWeight: (index: number, weight: number) => void;
  applyCorrectedWeights: (weights: number[]) => void;
  setCell: (expert: number, row: number, column: number, value: string) => void;
  applyImportedMatrix: (expert: number, matrix: string[][]) => void;
  applyImportedWorkbook: (matrices: string[][][]) => void;
  renameFactors: (names: string[]) => void;
  markAnswered: (step: StepId) => void;
  clearWeightsReset: () => void;
  setResults: (snapshot: AnalysisRequest, data: AnalysisData) => void;
  reset: () => void;
}

export const initialAnalysisState: AnalysisState = {
  solver: null,
  threshold: null,
  expertCount: null,
  factorCount: null,
  scale: null,
  factors: [],
  experts: [],
  matrices: [],
  answered: [],
  weightsReset: false,
  snapshot: null,
  snapshotHash: "",
  results: null,
};

/** Matrices for the current counts and scale, keeping existing cells. */
function fitMatrices(state: AnalysisState): string[][][] {
  const { scale, factorCount, expertCount, matrices } = state;
  if (!scale || !factorCount || !expertCount) return [];
  return Array.from({ length: expertCount }, (_, i) =>
    matrices[i]
      ? resizeMatrix(matrices[i], factorCount, scale)
      : createMatrix(factorCount, scale),
  );
}

export const useAnalysisStore = create<AnalysisState & AnalysisActions>()(
  (set) => ({
    ...initialAnalysisState,

    setSolver: (solver, scale) =>
      set((state) => {
        const familyChanged =
          state.scale !== null && state.scale.family !== scale.family;
        const next = {
          ...state,
          solver,
          scale,
          matrices: familyChanged ? [] : state.matrices,
        };
        return { solver, scale, matrices: fitMatrices(next) };
      }),

    setThreshold: (threshold) => set({ threshold }),

    setExpertCount: (count, weights) =>
      set((state) => {
        const experts = resizeNames(
          state.experts.map((expert) => expert.name),
          count,
          expertDefaultName,
        ).map((name, i) => ({ name, weight: weights[i] ?? 0 }));
        const next = { ...state, expertCount: count };
        return {
          expertCount: count,
          experts,
          matrices: fitMatrices(next).slice(0, count),
          // Removed experts' matrix steps are unanswered again if the count goes back up.
          answered: state.answered.filter((step) => {
            const index = matrixStepIndex(step);
            return index === null || index < count;
          }),
          weightsReset:
            state.expertCount !== null && state.expertCount !== count,
        };
      }),

    setFactorCount: (count) =>
      set((state) => ({
        factorCount: count,
        factors: resizeNames(state.factors, count, factorDefaultName),
        matrices: fitMatrices({ ...state, factorCount: count }),
      })),

    setFactorName: (index, name) =>
      set((state) => ({
        factors: state.factors.map((old, i) => (i === index ? name : old)),
      })),

    setExpertName: (index, name) =>
      set((state) => ({
        experts: state.experts.map((expert, i) =>
          i === index ? { ...expert, name } : expert,
        ),
      })),

    setExpertWeight: (index, weight) =>
      set((state) => ({
        experts: state.experts.map((expert, i) =>
          i === index ? { ...expert, weight } : expert,
        ),
      })),

    applyCorrectedWeights: (weights) =>
      set((state) => ({
        experts: state.experts.map((expert, i) => ({
          ...expert,
          weight: weights[i] ?? expert.weight,
        })),
      })),

    // Only the changed row is copied, so every other cell keeps its identity and does not re-render.
    setCell: (expert, row, column, value) =>
      set((state) => ({
        matrices: state.matrices.map((matrix, e) =>
          e !== expert
            ? matrix
            : matrix.map((cells, r) =>
                r !== row
                  ? cells
                  : cells.map((cell, c) => (c === column ? value : cell)),
              ),
        ),
      })),

    applyImportedMatrix: (expert, matrix) =>
      set((state) => ({
        matrices: state.matrices.map((old, e) =>
          e === expert && state.scale
            ? withDiagonal(matrix, state.scale.diagonalLabel)
            : old,
        ),
      })),

    applyImportedWorkbook: (matrices) =>
      set((state) => ({
        matrices: state.matrices.map((old, e) =>
          matrices[e] && state.scale
            ? withDiagonal(matrices[e], state.scale.diagonalLabel)
            : old,
        ),
      })),

    renameFactors: (names) =>
      set((state) => ({
        factors: state.factors.map((old, i) => names[i] ?? old),
      })),

    markAnswered: (step) =>
      set((state) =>
        state.answered.includes(step)
          ? state
          : { answered: [...state.answered, step] },
      ),

    clearWeightsReset: () => set({ weightsReset: false }),

    setResults: (snapshot, data) =>
      set({
        snapshot,
        snapshotHash: hashString(requestKey(snapshot)),
        results: data,
      }),

    reset: () => set(initialAnalysisState),
  }),
);
