import { useEffect } from "react";
import { toast } from "sonner";
import { REFRESH_NOTICE } from "@/constants/analysis.constants";

/**
 * Shows the "answers aren't saved" toast once per browser tab when the user reaches the notice step.
 * Session storage holds only a flag (never answers), so the toast does not return after a refresh.
 */
export function useRefreshNotice(step: string | undefined) {
  useEffect(() => {
    if (step !== REFRESH_NOTICE.STEP) return;
    try {
      if (sessionStorage.getItem(REFRESH_NOTICE.STORAGE_KEY)) return;
      sessionStorage.setItem(REFRESH_NOTICE.STORAGE_KEY, "1");
    } catch {
      // Storage blocked (private mode): still show it, at most once per page load.
    }
    toast.info(REFRESH_NOTICE.TITLE, {
      description: REFRESH_NOTICE.DESCRIPTION,
      duration: REFRESH_NOTICE.DURATION_MS,
      closeButton: true,
    });
  }, [step]);
}
