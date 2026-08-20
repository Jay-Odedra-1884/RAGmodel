import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Voice RAG — HH Goa 2026",
  description: "Voice-enabled Retrieval-Augmented Generation pipeline",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
