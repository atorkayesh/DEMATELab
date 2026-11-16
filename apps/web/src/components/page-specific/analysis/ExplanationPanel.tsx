import { SparklesIcon } from "lucide-react";
import { useState } from "react";
import { AzureEndpointDialog } from "@/components/page-specific/analysis/AzureEndpointDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  AZURE_PROVIDER,
  DEFAULT_MODELS,
  EXPLANATION_STATUS,
  EXPLANATION_TEXT,
} from "@/constants/explanation.constants";
import { useExplanation } from "@/hooks/explanation.hook";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import { PROVIDERS, type Provider } from "@/interfaces/explanation.interface";
import { errorMessage } from "@/utils/api.utils";

const FIELD_CLASS = "flex min-w-0 flex-1 basis-48 flex-col gap-1 text-sm";

/**
 * AI explanation of the results snapshot. The API key stays in this component's state and is only
 * sent in the request body; the Azure endpoint is remembered while these results stay.
 */
export function ExplanationPanel({ snapshot }: { snapshot: AnalysisRequest }) {
  const [provider, setProvider] = useState<Provider>(PROVIDERS[0]);
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState<string>(DEFAULT_MODELS[PROVIDERS[0]]);
  const [azureEndpoint, setAzureEndpoint] = useState("");
  const [askEndpoint, setAskEndpoint] = useState(false);
  const [status, setStatus] = useState("");
  const [output, setOutput] = useState("");
  const explanation = useExplanation();
  const isAzure = provider === AZURE_PROVIDER;

  const send = (endpoint: string | null) => {
    setStatus(EXPLANATION_STATUS.PENDING);
    setOutput("");
    explanation.generate(
      {
        analysis: snapshot,
        provider,
        api_key: apiKey.trim(),
        model: model.trim() || null,
        azure_endpoint: endpoint,
      },
      // As in Qt: "Done" with the text, or "Error" with the API's message in the output area.
      {
        onSuccess: (data) => {
          setStatus(EXPLANATION_STATUS.DONE);
          setOutput(data.text);
        },
        onError: (error) => {
          setStatus(EXPLANATION_STATUS.ERROR);
          setOutput(errorMessage(error));
        },
      },
    );
  };

  const start = () => {
    if (!apiKey.trim()) {
      setStatus(EXPLANATION_STATUS.MISSING_KEY);
      return;
    }
    if (isAzure) setAskEndpoint(true);
    else send(null);
  };

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h3 className="font-semibold">{EXPLANATION_TEXT.TITLE}</h3>
        <p className="text-sm text-muted-foreground">{EXPLANATION_TEXT.NOTE}</p>
      </div>
      <div className="flex flex-wrap gap-3">
        <label className={FIELD_CLASS}>
          {EXPLANATION_TEXT.ENGINE}
          <select
            value={provider}
            onChange={(event) => {
              const next = event.target.value as Provider;
              setProvider(next);
              setModel(DEFAULT_MODELS[next]);
            }}
            className="h-8 rounded-lg border border-input bg-card px-2"
          >
            {PROVIDERS.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <label className={FIELD_CLASS}>
          {EXPLANATION_TEXT.API_KEY}
          <Input
            type="password"
            autoComplete="off"
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
          />
        </label>
        <label className={FIELD_CLASS}>
          {EXPLANATION_TEXT.MODEL}
          <Input
            value={model}
            placeholder={
              isAzure
                ? EXPLANATION_TEXT.AZURE_MODEL_PLACEHOLDER
                : EXPLANATION_TEXT.MODEL_PLACEHOLDER
            }
            onChange={(event) => setModel(event.target.value)}
          />
        </label>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <Button type="button" onClick={start} disabled={explanation.isPending}>
          <SparklesIcon data-icon="inline-start" />
          {EXPLANATION_TEXT.GENERATE}
        </Button>
        <output className="text-sm text-muted-foreground">{status}</output>
      </div>
      <output
        aria-label={EXPLANATION_TEXT.OUTPUT_LABEL}
        className="block min-h-40 rounded-lg border bg-card p-3 text-sm whitespace-pre-wrap wrap-break-word"
      >
        {output}
      </output>
      {askEndpoint && (
        <AzureEndpointDialog
          open
          initialEndpoint={azureEndpoint}
          onSubmit={(endpoint) => {
            setAskEndpoint(false);
            if (!endpoint) {
              setStatus(EXPLANATION_STATUS.MISSING_ENDPOINT);
              return;
            }
            setAzureEndpoint(endpoint);
            send(endpoint);
          }}
          onCancel={() => {
            setAskEndpoint(false);
            setStatus(EXPLANATION_STATUS.MISSING_ENDPOINT);
          }}
        />
      )}
    </div>
  );
}
