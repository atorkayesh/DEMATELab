export const APP_NAME = "DEMATELab";

export const APP_SUBTITLE = "Cause and Effect Analysis";

/** The app name for the footer credit. */
export const APP_FULL_NAME = "DEMATELab";

/** Footer credit: the app name, then the research centre (linked), then the year. */
export const FOOTER_LINKS: readonly { label: string; href: string }[] = [
  { label: "Forschungszentrum Jülich", href: "https://www.fz-juelich.de/en" },
];

/** The logo, served from `public/`. */
export const APP_LOGO_PATH = "/logo.png";

export const PAGE_TITLES = {
  HOME: `${APP_NAME} · ${APP_SUBTITLE}`,
  STATUS: `Status · ${APP_NAME}`,
} as const;

export const NOT_FOUND_TEXT = {
  TITLE: "Page not found",
  BODY: "This page does not exist.",
  LINK: "Go to the analysis",
} as const;
