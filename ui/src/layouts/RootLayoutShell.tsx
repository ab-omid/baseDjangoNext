import { PropsWithChildren } from "react";

import { AppProviders } from "@/components/AppProviders";

/**
 * Defines the application root HTML shell and provider tree.
 *
 * Where: Mounted by `app/layout.tsx` as the single root layout
 * Uses: `AppProviders` for theme and query context
 * Behavior: Wraps all routes with shared html/body structure and providers
 */
export function RootLayoutShell({ children }: PropsWithChildren) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
