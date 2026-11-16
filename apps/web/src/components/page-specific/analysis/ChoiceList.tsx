import type { KeyboardEvent } from "react";
import type { Option } from "@/interfaces/scales.interface";
import { cn } from "@/lib/utils";

/** Letter shown before option `index` (A, B, C, …), Typeform style. */
const letterFor = (index: number) => String.fromCharCode(65 + index);

/**
 * Single choice as large radio rows. Arrow keys move and select (native radios); pressing an
 * option's letter selects it.
 */
export function ChoiceList({
  name,
  label,
  options,
  value,
  onChange,
}: {
  name: string;
  label: string;
  options: readonly Option[];
  value: string;
  onChange: (key: string) => void;
}) {
  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (
      event.key.length !== 1 ||
      event.metaKey ||
      event.ctrlKey ||
      event.altKey
    ) {
      return;
    }
    const index = event.key.toUpperCase().charCodeAt(0) - 65;
    const option = options[index];
    if (!option) return;
    event.preventDefault();
    onChange(option.key);
    event.currentTarget
      .querySelector<HTMLInputElement>(
        `input[value="${CSS.escape(option.key)}"]`,
      )
      ?.focus();
  };

  return (
    <div
      role="radiogroup"
      aria-label={label}
      onKeyDown={handleKeyDown}
      className="flex flex-col gap-2"
    >
      {options.map((option, index) => {
        const checked = option.key === value;
        return (
          <label
            key={option.key}
            className={cn(
              "flex cursor-pointer items-center gap-3 rounded-lg border bg-card px-3 py-2.5 transition-colors has-focus-visible:ring-3 has-focus-visible:ring-ring/50",
              checked ? "border-primary bg-accent" : "hover:bg-muted",
            )}
          >
            <input
              type="radio"
              name={name}
              value={option.key}
              checked={checked}
              onChange={() => onChange(option.key)}
              className="sr-only"
            />
            <span
              aria-hidden="true"
              className={cn(
                "flex size-6 shrink-0 items-center justify-center rounded border text-xs font-semibold",
                checked && "border-primary bg-primary text-primary-foreground",
              )}
            >
              {letterFor(index)}
            </span>
            <span className="font-medium">{option.label}</span>
          </label>
        );
      })}
    </div>
  );
}
