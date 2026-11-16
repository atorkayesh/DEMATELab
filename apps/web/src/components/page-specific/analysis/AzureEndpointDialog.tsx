import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { AZURE_DIALOG_TEXT } from "@/constants/explanation.constants";

/** Qt's "Azure OpenAI Endpoint" prompt; OK returns the trimmed endpoint (empty means none). */
export function AzureEndpointDialog({
  open,
  initialEndpoint,
  onSubmit,
  onCancel,
}: {
  open: boolean;
  initialEndpoint: string;
  onSubmit: (endpoint: string) => void;
  onCancel: () => void;
}) {
  const [endpoint, setEndpoint] = useState(initialEndpoint);

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (!next) onCancel();
      }}
    >
      <DialogContent className="sm:max-w-lg">
        <form
          className="flex flex-col gap-4"
          onSubmit={(event) => {
            event.preventDefault();
            onSubmit(endpoint.trim());
          }}
        >
          <DialogHeader>
            <DialogTitle>{AZURE_DIALOG_TEXT.TITLE}</DialogTitle>
            <DialogDescription>
              {AZURE_DIALOG_TEXT.PROMPT}
              <br />
              {AZURE_DIALOG_TEXT.EXAMPLE}
            </DialogDescription>
          </DialogHeader>
          <Input
            aria-label={AZURE_DIALOG_TEXT.TITLE}
            value={endpoint}
            placeholder={AZURE_DIALOG_TEXT.PLACEHOLDER}
            onChange={(event) => setEndpoint(event.target.value)}
          />
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onCancel}>
              {AZURE_DIALOG_TEXT.CANCEL}
            </Button>
            <Button type="submit">{AZURE_DIALOG_TEXT.OK}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
