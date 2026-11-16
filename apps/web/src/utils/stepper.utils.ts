/**
 * Qt's stepper rule on blur: clamp to `[min, max]`; text that is not a number, or not an integer
 * when `decimals` is 0, resets to the minimum. Decimal values are rounded to `decimals`.
 */
export function clampStepperValue(
  text: string,
  min: number,
  max: number,
  decimals: number,
): number {
  const parsed = Number(text.trim());
  if (text.trim() === "" || !Number.isFinite(parsed)) return min;
  if (decimals === 0 && !Number.isInteger(parsed)) return min;
  const rounded = Number(parsed.toFixed(decimals));
  return Math.min(max, Math.max(min, rounded));
}
