import { ChevronDownIcon, ChevronUpIcon } from "lucide-react";
import { useState } from "react";
import { flushSync } from "react-dom";
import { Input } from "@/components/ui/input";
import { FIELD_LABELS } from "@/constants/analysis.constants";
import { clampStepperValue } from "@/utils/stepper.utils";

/**
 * Number field with ▲/▼ buttons (Qt's stepper). Typing a valid value inside the range updates it at
 * once; on blur the text is clamped to the range, and a non-number (or a non-integer when
 * `decimals` is 0) resets to the minimum, as in Qt. Enter commits the same way before the form
 * handles it.
 */
export function NumberStepper({
  id,
  label,
  value,
  min,
  max,
  step = 1,
  decimals = 0,
  onChange,
  className,
}: {
  id: string;
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  decimals?: number;
  onChange: (value: number) => void;
  className?: string;
}) {
  const format = (number: number) => number.toFixed(decimals);
  const [text, setText] = useState(format(value));
  // Show a new value from the parent (e.g. corrected weights) without losing what is being typed.
  const [previousValue, setPreviousValue] = useState(value);
  if (value !== previousValue) {
    setPreviousValue(value);
    if (Number(text) !== value) setText(format(value));
  }

  const commit = (next: number) => {
    setText(format(next));
    onChange(next);
  };
  const stepBy = (direction: 1 | -1) =>
    commit(
      clampStepperValue(String(value + direction * step), min, max, decimals),
    );

  return (
    <div className={className ?? "flex w-40 items-stretch"}>
      <Input
        id={id}
        aria-label={label}
        inputMode={decimals > 0 ? "decimal" : "numeric"}
        value={text}
        className="rounded-r-none"
        onChange={(event) => {
          setText(event.target.value);
          const parsed = Number(event.target.value);
          const valid =
            event.target.value.trim() !== "" &&
            Number.isFinite(parsed) &&
            parsed >= min &&
            parsed <= max &&
            (decimals > 0 || Number.isInteger(parsed));
          if (valid) onChange(parsed);
        }}
        onBlur={() => commit(clampStepperValue(text, min, max, decimals))}
        onKeyDown={(event) => {
          if (event.key === "ArrowUp") {
            event.preventDefault();
            stepBy(1);
          } else if (event.key === "ArrowDown") {
            event.preventDefault();
            stepBy(-1);
          } else if (event.key === "Enter") {
            // Commit the clamped value before the form continues with it (no preventDefault).
            flushSync(() =>
              commit(clampStepperValue(text, min, max, decimals)),
            );
          }
        }}
      />
      <div className="flex flex-col">
        <button
          type="button"
          tabIndex={-1}
          aria-label={`${FIELD_LABELS.INCREASE} ${label}`}
          onClick={() => stepBy(1)}
          className="flex h-4 w-7 items-center justify-center rounded-tr-lg border border-l-0 border-input hover:bg-muted"
        >
          <ChevronUpIcon className="size-3" />
        </button>
        <button
          type="button"
          tabIndex={-1}
          aria-label={`${FIELD_LABELS.DECREASE} ${label}`}
          onClick={() => stepBy(-1)}
          className="flex h-4 w-7 items-center justify-center rounded-br-lg border border-t-0 border-l-0 border-input hover:bg-muted"
        >
          <ChevronDownIcon className="size-3" />
        </button>
      </div>
    </div>
  );
}
