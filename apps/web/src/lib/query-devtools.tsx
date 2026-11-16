import { ReactQueryDevtoolsPanel } from "@tanstack/react-query-devtools";

export const queryDevtoolsPlugin = {
  name: "TanStack Query",
  render: <ReactQueryDevtoolsPanel />,
};
