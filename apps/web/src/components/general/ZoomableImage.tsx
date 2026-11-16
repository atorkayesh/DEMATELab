import { ZoomInIcon, ZoomOutIcon } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { RESULTS_TEXT, ZOOM_STEP } from "@/constants/results.constants";

/** An image in a scroll box with Zoom In / Zoom Out (1.2× per click, as in Qt). */
export function ZoomableImage({ src, alt }: { src: string; alt: string }) {
  const [zoom, setZoom] = useState(1);

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => setZoom((value) => value * ZOOM_STEP)}
        >
          <ZoomInIcon data-icon="inline-start" />
          {RESULTS_TEXT.ZOOM_IN}
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => setZoom((value) => value / ZOOM_STEP)}
        >
          <ZoomOutIcon data-icon="inline-start" />
          {RESULTS_TEXT.ZOOM_OUT}
        </Button>
      </div>
      <div className="max-h-[70vh] overflow-auto rounded-lg border bg-white">
        <img
          src={src}
          alt={alt}
          style={{ width: `${zoom * 100}%`, maxWidth: "none" }}
          className="block h-auto"
        />
      </div>
    </div>
  );
}
