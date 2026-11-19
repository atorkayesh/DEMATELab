import { LockIcon, SparklesIcon } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { InlineError } from "@/components/general/InlineError";
import { AzureEndpointDialog } from "@/components/page-specific/analysis/AzureEndpointDialog";
import { ExplanationSettings } from "@/components/page-specific/analysis/ExplanationSettings";
import { Button } from "@/components/ui/button";
import {
  EXPLANATION_STATUS,
  EXPLANATION_TEXT,
  EXPLANATION_TOAST,
} from "@/constants/explanation.constants";
import {
  useExplanation,
  useExplanationProviders,
} from "@/hooks/explanation.hook";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import { errorMessage } from "@/utils/api.utils";

/**
 * AI explanation of the results snapshot. The API key stays in this component's state and is only
 * sent in the request body; the Azure endpoint is remembered while these results stay. Providers and
 * models come from the API; a provider change resets the model to its default (Azure: empty).
 * Failures are shown in a toast; the status line shows progress.
 */
export function ExplanationPanel({ snapshot }: { snapshot: AnalysisRequest }) {
  const providers = useExplanationProviders();
  const [providerId, setProviderId] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState("");
  // null = the provider's default model (empty for Azure's free-text deployment name).
  const [modelChoice, setModelChoice] = useState<string | null>(null);
  const [azureEndpoint, setAzureEndpoint] = useState("");
  const [askEndpoint, setAskEndpoint] = useState(false);
  const [status, setStatus] = useState("");
  const [output, setOutput] = useState("");
  const explanation = useExplanation();
  const list = providers.data ?? [];
  const provider = list.find((item) => item.id === providerId) ?? list[0];
  const model = modelChoice ?? provider?.default_model ?? "";
  const isAzure = provider?.free_text_model ?? false;
  const canGenerate =
    !!provider && !explanation.isPending && (!isAzure || !!model.trim());

  const send = (endpoint: string | null) => {
    if (!provider) return;
    setStatus(EXPLANATION_STATUS.PENDING);
    setOutput("");
    explanation.generate(
      {
        analysis: snapshot,
        provider: provider.id,
        api_key: apiKey.trim(),
        model: model.trim() || null,
        azure_endpoint: endpoint,
      },
      // "Done" with the text, or "Error" with the API's message in a toast.
      {
        onSuccess: (data) => {
          setStatus(EXPLANATION_STATUS.DONE);
          setOutput(data.text);
        },
        onError: (error) => {
          setStatus(EXPLANATION_STATUS.ERROR);
          toast.error(EXPLANATION_TOAST.ERROR_TITLE, {
            description: errorMessage(error),
          });
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
      <p className="flex items-start gap-1.5 text-xs text-muted-foreground">
        <LockIcon className="mt-px size-3.5 shrink-0" aria-hidden="true" />
        {EXPLANATION_TEXT.KEY_PRIVACY}
      </p>
      <InlineError
        message={providers.isError ? EXPLANATION_TEXT.PROVIDERS_ERROR : null}
      />
      {provider && (
        <ExplanationSettings
          providers={list}
          provider={provider}
          apiKey={apiKey}
          model={model}
          onProviderChange={(id) => {
            setProviderId(id);
            setModelChoice(null);
          }}
          onApiKeyChange={setApiKey}
          onModelChange={setModelChoice}
        />
      )}
      <div className="flex flex-wrap items-center gap-3">
        <Button type="button" onClick={start} disabled={!canGenerate}>
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
