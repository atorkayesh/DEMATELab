import { InlineError } from "@/components/general/InlineError";
import { ZoomableImage } from "@/components/general/ZoomableImage";
import { RESULTS_TEXT } from "@/constants/results.constants";
import { useObjectUrl } from "@/hooks/object-url.hook";
import { errorMessage } from "@/utils/api.utils";

/** A chart PNG from the API: loading text, the API's error, or the zoomable image. */
export function ChartImage({
  blob,
  isPending,
  error,
  alt,
}: {
  blob: Blob | undefined;
  isPending: boolean;
  error: unknown;
  alt: string;
}) {
  const url = useObjectUrl(blob);
  if (error) return <InlineError message={errorMessage(error)} />;
  if (isPending || !url) {
    return (
      <p className="text-sm text-muted-foreground">
        {RESULTS_TEXT.LOADING_CHART}
      </p>
    );
  }
  return <ZoomableImage src={url} alt={alt} />;
}
