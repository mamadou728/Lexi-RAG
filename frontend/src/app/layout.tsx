import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lexi-RAG - Legal Workspace",
  description: "Legal document analysis and chat interface",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
