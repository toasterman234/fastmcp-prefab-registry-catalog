import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FastMCP Workspace",
  description: "Workspace shell for the FastMCP registry, Prefab apps, artifacts, runs, and review.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
