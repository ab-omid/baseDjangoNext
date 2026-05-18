import type { Metadata } from "next";

import { RootLayoutShell } from "@/layouts/RootLayoutShell";

import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "PDNR",
  description: "PDNR frontend",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <RootLayoutShell>{children}</RootLayoutShell>;
}
