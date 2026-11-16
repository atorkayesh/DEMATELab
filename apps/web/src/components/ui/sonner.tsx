import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
} from "lucide-react";
import type { CSSProperties } from "react";
import { Toaster as Sonner, type ToasterProps } from "sonner";

/**
 * Shadcn's Sonner toaster themed for DEMATELab: warm-white card, navy text, our border, radius and
 * Manrope, the destructive colour for errors. Light only (the app has no theme switch, so no
 * `next-themes`). Bottom-right on desktop; on phones Sonner spans the width inside `mobileOffset`.
 */
const Toaster = ({ ...props }: ToasterProps) => {
  return (
    <Sonner
      theme="light"
      position="bottom-right"
      mobileOffset={12}
      className="toaster group font-sans"
      icons={{
        success: <CircleCheckIcon className="size-4" />,
        info: <InfoIcon className="size-4" />,
        warning: <TriangleAlertIcon className="size-4" />,
        error: <OctagonXIcon className="size-4" />,
        loading: <Loader2Icon className="size-4 animate-spin" />,
      }}
      style={
        {
          "--normal-bg": "var(--card)",
          "--normal-text": "var(--card-foreground)",
          "--normal-border": "var(--border)",
          "--border-radius": "var(--radius)",
        } as CSSProperties
      }
      toastOptions={{
        classNames: {
          toast: "cn-toast font-sans text-sm shadow-md wrap-break-word",
          description: "!text-card-foreground",
          error:
            "!border-destructive/40 [&_[data-icon]]:!text-destructive [&_[data-title]]:!text-destructive",
        },
      }}
      {...props}
    />
  );
};

export { Toaster };
