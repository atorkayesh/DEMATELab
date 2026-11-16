import { renderHook } from "@testing-library/react";
import { toast } from "sonner";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { REFRESH_NOTICE } from "@/constants/analysis.constants";
import { useRefreshNotice } from "@/hooks/refresh-notice.hook";

vi.mock("sonner", () => ({ toast: { info: vi.fn() } }));

describe("useRefreshNotice", () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.mocked(toast.info).mockClear();
  });

  it("stays quiet before the notice step", () => {
    renderHook(() => useRefreshNotice("threshold"));
    expect(toast.info).not.toHaveBeenCalled();
  });

  it("shows the toast once per tab session", () => {
    const first = renderHook(() => useRefreshNotice(REFRESH_NOTICE.STEP));
    first.unmount();
    renderHook(() => useRefreshNotice(REFRESH_NOTICE.STEP));
    expect(toast.info).toHaveBeenCalledTimes(1);
    expect(toast.info).toHaveBeenCalledWith(
      REFRESH_NOTICE.TITLE,
      expect.objectContaining({ description: REFRESH_NOTICE.DESCRIPTION }),
    );
  });
});
