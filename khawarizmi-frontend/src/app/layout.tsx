import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/providers";
import { OnboardingOverlay } from "@/components/gamification/OnboardingOverlay";

export const metadata: Metadata = {
  title: "الخوارزمي برو — بكالوريا جزائرية",
  description: "مرافقك الذكي لنجاح بكالوريا علوم الطبيعة والحياة",
  icons: undefined,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="ar"
      dir="rtl"
      className="h-full antialiased"
      suppressHydrationWarning
    >
      <head>
        <link rel="manifest" href="/manifest.json" />
      </head>
      <body className="min-h-full flex flex-col" suppressHydrationWarning>
        <Providers>{children}</Providers>
        <OnboardingOverlay />
      </body>
    </html>
  );
}
