import type { ReactNode } from "react";
import { AppFooter } from "@/components/general/AppFooter";
import { AppHeader } from "@/components/general/AppHeader";

/**
 * Frame of every page: header, the page, and the footer, centred and at most `max-w-layout`
 * (1200px) wide. The page fills the height between header and footer (`dvh`, so mobile browser
 * bars are accounted for); pages set their own narrower column width inside it.
 */
export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-layout flex-col">
      <AppHeader />
      <main className="flex w-full flex-1 flex-col items-center px-4 sm:px-6">
        {children}
      </main>
      <AppFooter />
    </div>
  );
}
