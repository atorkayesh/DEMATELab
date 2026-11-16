import { createFileRoute } from "@tanstack/react-router";
import { PageHeader } from "@/components/general/PageHeader";
import { ApiHealthCard } from "@/components/page-specific/status/ApiHealthCard";
import { APP_NAME, PAGE_TITLES } from "@/constants/layout.constants";

export const Route = createFileRoute("/status")({
  head: () => ({ meta: [{ title: PAGE_TITLES.STATUS }] }),
  component: Status,
});

function Status() {
  return (
    <div className="flex w-full max-w-2xl flex-col gap-6 pb-8">
      <PageHeader>
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          {APP_NAME} Status
        </h1>
      </PageHeader>
      <ApiHealthCard />
    </div>
  );
}
