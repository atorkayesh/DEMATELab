import { Link } from "@tanstack/react-router";
import { PageHeader } from "@/components/general/PageHeader";
import { NOT_FOUND_TEXT } from "@/constants/layout.constants";

/** 404 page for unknown routes. */
export function NotFound() {
  return (
    <div className="flex w-full max-w-2xl flex-col gap-4 pb-8">
      <PageHeader>
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          {NOT_FOUND_TEXT.TITLE}
        </h1>
        <p className="text-muted-foreground">{NOT_FOUND_TEXT.BODY}</p>
      </PageHeader>
      <Link to="/" className="underline underline-offset-4">
        {NOT_FOUND_TEXT.LINK}
      </Link>
    </div>
  );
}
