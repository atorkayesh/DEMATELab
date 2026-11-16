import type { FixedStepId } from "@/interfaces/analysis.interface";

/** Qt's card subtitles, shown as helper text on the steps that came from each card. */
const SETUP_HELP =
  "Choose your preferred solver and threshold identifier. The number of experts and factors can be defined subsequently.";
const FACTORS_HELP =
  "Define the factors to be analyzed and specify expert weights.";
export const MATRIX_HELP =
  "Diagonal cells are fixed to the solver-specific no-influence value because a factor cannot directly influence itself.";

/** Question, short label (step list) and helper text of each fixed step. */
export const STEP_TEXT: Record<
  FixedStepId,
  { title: string; label: string; help?: string }
> = {
  solver: { title: "Solver type", label: "Solver", help: SETUP_HELP },
  threshold: {
    title: "Threshold method",
    label: "Threshold",
    help: SETUP_HELP,
  },
  experts: {
    title: "Number of experts",
    label: "Experts",
    help: SETUP_HELP,
  },
  factors: {
    title: "Number of factors",
    label: "Factors",
    help: SETUP_HELP,
  },
  "factor-names": {
    title: "Factor names",
    label: "Factor names",
    help: FACTORS_HELP,
  },
  "expert-weights": {
    title: "Experts and Weights",
    label: "Weights",
    help: FACTORS_HELP,
  },
  review: {
    title: "Review and run",
    label: "Review",
    help: "Check your answers, then run the analysis.",
  },
  results: { title: "Results", label: "Results" },
};

/** Title of expert `index`'s matrix step. */
export function matrixStepTitle(index: number, count: number, name: string) {
  return `Expert ${index + 1} of ${count}: ${name}`;
}

export const MATRIX_STEP_QUESTION =
  "How does each factor (row) influence the others (columns)?";

/** Short label of a matrix step in the step list. */
export function matrixStepLabel(index: number) {
  return `Matrix ${index + 1}`;
}

/** Default names, as in Qt. */
export const factorDefaultName = (index: number) => `F${index + 1}`;
export const expertDefaultName = (index: number) => `Expert ${index + 1}`;

export const FLOW_TEXT = {
  BACK: "Back",
  NEXT: "OK",
  RUN: "Run Analysis",
  RUNNING: "Running analysis…",
  BACK_TO_INPUTS: "Back to inputs",
  EDIT: "Edit",
  STEPS_LABEL: "Steps",
  PROGRESS_LABEL: "Progress",
  KEYBOARD_HINT: "press Enter ↵",
  LOADING: "Loading the analysis options…",
  LOAD_FAILED: "The analysis options could not be loaded from the API.",
  RETRY: "Try again",
  WEIGHTS_RESET_NOTE:
    "The number of experts changed, so the weights were reset to equal defaults.",
} as const;

/** Qt's validation messages. */
export const VALIDATION_MESSAGES = {
  FACTORS_EMPTY: "All factor names must be filled.",
  EXPERTS_EMPTY: "All expert names must be filled.",
  FACTORS_DUPLICATE: "Factor names must be unique.",
  WEIGHTS_SUM: "Expert weights must sum to 1.",
} as const;

export const FIELD_LABELS = {
  EXPERT_NAME: (index: number) => `Expert ${index + 1} name`,
  EXPERT_WEIGHT: (index: number) => `Expert ${index + 1} weight`,
  FACTOR_NAME: (index: number) => `Factor ${index + 1} name`,
  INCREASE: "Increase",
  DECREASE: "Decrease",
} as const;

/** Qt's "Solver Change Detected" dialog. */
export const SOLVER_CHANGE_TEXT = {
  TITLE: "Solver Change Detected",
  TO_Z: [
    "The current matrix uses standard linguistic judgments and is not valid for Fuzzy Z-DEMATEL.",
    "Fuzzy Z-DEMATEL requires combined influence–reliability judgments.",
    "The matrix editor will be regenerated and current matrix values will be lost.",
  ],
  TO_STANDARD: [
    "The current matrix uses combined influence–reliability judgments and is not valid for the selected solver.",
    "The matrix editor will be regenerated and current matrix values will be lost.",
  ],
  CONFIRM: "OK",
  CANCEL: "Cancel",
} as const;

/** Confirmation when fewer factors or experts would drop edited matrix cells. */
export const RESET_CONFIRM_TEXT = {
  TITLE: "Discard matrix values?",
  FACTORS:
    "The removed factors have matrix values that will be lost. Continue?",
  EXPERTS:
    "The removed experts have matrix values that will be lost. Continue?",
  CONFIRM: "Continue",
  CANCEL: "Cancel",
} as const;

/** Review step: the answer rows. */
export const REVIEW_LABELS = {
  SOLVER: "Solver type",
  THRESHOLD: "Threshold method",
  EXPERTS: "Experts and weights",
  FACTORS: "Factors",
  MATRICES: "Matrices",
  EDITED_CELLS: (count: number) =>
    `${count} edited ${count === 1 ? "cell" : "cells"}`,
} as const;

/** Qt's import texts. */
export const IMPORT_TEXT = {
  MATRIX: "Import Matrix from XLSX",
  ALL: "Import All Experts from XLSX",
  ACCEPT: ".xlsx",
  FAILED: (message: string) => `Import failed: ${message}`,
  NOT_AVAILABLE_TITLE: "Import Not Available",
  NOT_AVAILABLE:
    "XLSX import currently supports only the standard linguistic scale:\nNo influence, Low influence, Medium influence, High influence, Extreme influence.",
} as const;

/** Matrix grid sizes in pixels (the virtualiser needs fixed sizes). */
export const MATRIX_GRID = {
  ROW_HEIGHT: 40,
  HEADER_HEIGHT: 40,
  ROW_HEADER_WIDTH: 160,
  CELL_WIDTH: { standard: 170, fuzzy_z: 300 },
  OVERSCAN: 4,
  /** Initial viewport before layout (also used in tests, where there is no layout). */
  INITIAL_RECT: { width: 1000, height: 480 },
} as const;

/** "Start over": clears every answer, matrix and result and returns to the first step. */
export const START_OVER_TEXT = {
  BUTTON: "Start over",
  TITLE: "Start over?",
  DESCRIPTION: "All answers, matrices and results will be cleared.",
  CONFIRM: "Start over",
  CANCEL: "Cancel",
} as const;
