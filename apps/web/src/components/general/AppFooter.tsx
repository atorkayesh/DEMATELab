import { Fragment } from "react";
import { APP_FULL_NAME, FOOTER_LINKS } from "@/constants/layout.constants";

/** Muted credit line at the bottom of every page; wraps onto several lines on small screens. */
export function AppFooter() {
  return (
    <footer className="flex flex-wrap items-center justify-center gap-x-1.5 gap-y-1 px-4 pt-6 pb-8 text-center text-[0.75rem] text-muted-foreground sm:px-6">
      <span>{APP_FULL_NAME}</span>
      {FOOTER_LINKS.map((link) => (
        <Fragment key={link.href}>
          <span aria-hidden="true">·</span>
          <a
            href={link.href}
            target="_blank"
            rel="noopener noreferrer"
            className="underline-offset-2 hover:text-foreground hover:underline"
          >
            {link.label}
          </a>
        </Fragment>
      ))}
      <span aria-hidden="true">·</span>
      <span>{new Date().getFullYear()}</span>
    </footer>
  );
}
