import { VALIDATION_MESSAGES } from "@/constants/analysis.constants";

/** Qt's factor-name checks: every name filled (after trimming), unique (case-sensitive). */
export function validateFactorNames(names: string[]): string | null {
  const trimmed = names.map((name) => name.trim());
  if (trimmed.some((name) => !name)) return VALIDATION_MESSAGES.FACTORS_EMPTY;
  if (new Set(trimmed).size !== trimmed.length) {
    return VALIDATION_MESSAGES.FACTORS_DUPLICATE;
  }
  return null;
}

/** Qt's expert-name check: every name filled (duplicates are allowed). */
export function validateExpertNames(names: string[]): string | null {
  return names.some((name) => !name.trim())
    ? VALIDATION_MESSAGES.EXPERTS_EMPTY
    : null;
}

/** All name checks, in Qt's order (factors first). */
export function validateNames(
  factorNames: string[],
  expertNames: string[],
): string | null {
  return validateFactorNames(factorNames) ?? validateExpertNames(expertNames);
}
