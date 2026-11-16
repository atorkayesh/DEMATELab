import { Link } from "@tanstack/react-router";
import {
  APP_LOGO_PATH,
  APP_NAME,
  APP_SUBTITLE,
} from "@/constants/layout.constants";

/** Top bar on every page: the logo, "DEMATELab" and its subtitle. The app has one page, so no nav. */
export function AppHeader() {
  return (
    <header className="flex w-full items-center px-4 pt-5 sm:px-6">
      <Link to="/" className="flex min-w-0 items-center gap-2.5">
        <img
          src={APP_LOGO_PATH}
          alt=""
          width={32}
          height={32}
          className="size-8 shrink-0 rounded-md"
        />
        <span className="flex min-w-0 flex-col leading-tight">
          <span className="text-[0.95rem] font-bold tracking-[-0.03em]">
            {APP_NAME}
          </span>
          <span className="truncate text-xs text-muted-foreground">
            {APP_SUBTITLE}
          </span>
        </span>
      </Link>
    </header>
  );
}
