import { ApiKeyInput } from "@/components/page-specific/analysis/ApiKeyInput";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { EXPLANATION_TEXT } from "@/constants/explanation.constants";
import type { ExplanationProvider } from "@/interfaces/explanation.interface";

const FIELD_CLASS = "flex min-w-0 flex-1 basis-48 flex-col gap-1 text-sm";
const TRIGGER_CLASS = "h-8 w-full bg-card text-base max-sm:h-11 md:text-sm";
const ITEM_CLASS = "text-base md:text-sm";

/**
 * AI provider, API key and model fields. The model is a select of the provider's models from the
 * API, except Azure OpenAI, where it is the user's free-text deployment name.
 */
const API_KEY_ID = "explanation-api-key";

export function ExplanationSettings({
  providers,
  provider,
  apiKey,
  model,
  onProviderChange,
  onApiKeyChange,
  onModelChange,
}: {
  providers: ExplanationProvider[];
  provider: ExplanationProvider;
  apiKey: string;
  model: string;
  onProviderChange: (id: string) => void;
  onApiKeyChange: (value: string) => void;
  onModelChange: (value: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-3">
      <div className={FIELD_CLASS}>
        {EXPLANATION_TEXT.PROVIDER}
        <Select
          value={provider.id}
          onValueChange={(next) => next && onProviderChange(next)}
        >
          <SelectTrigger
            aria-label={EXPLANATION_TEXT.PROVIDER}
            className={TRIGGER_CLASS}
          >
            <SelectValue />
          </SelectTrigger>
          <SelectContent alignItemWithTrigger={false}>
            {providers.map((item) => (
              <SelectItem key={item.id} value={item.id} className={ITEM_CLASS}>
                {item.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <label className={FIELD_CLASS} htmlFor={API_KEY_ID}>
        {EXPLANATION_TEXT.API_KEY}
        <ApiKeyInput id={API_KEY_ID} value={apiKey} onChange={onApiKeyChange} />
      </label>
      {provider.free_text_model ? (
        <label className={FIELD_CLASS}>
          {EXPLANATION_TEXT.MODEL}
          <Input
            value={model}
            placeholder={EXPLANATION_TEXT.AZURE_MODEL_PLACEHOLDER}
            onChange={(event) => onModelChange(event.target.value)}
          />
        </label>
      ) : (
        <div className={FIELD_CLASS}>
          {EXPLANATION_TEXT.MODEL}
          <Select
            value={model}
            onValueChange={(next) => next && onModelChange(next)}
          >
            <SelectTrigger
              aria-label={EXPLANATION_TEXT.MODEL}
              className={TRIGGER_CLASS}
            >
              <SelectValue />
            </SelectTrigger>
            <SelectContent alignItemWithTrigger={false}>
              {provider.models.map((name) => (
                <SelectItem key={name} value={name} className={ITEM_CLASS}>
                  {name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}
    </div>
  );
}
