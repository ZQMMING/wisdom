import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "TONGSHU — Dein Weg durch den Tag",
  description: "Tägliche östliche Weisheit, persönlich für dich berechnet. Dein I Ging Begleiter.",
  manifest: "/manifest.json",
  themeColor: "#08090a",
  appleWebApp: { capable: true, statusBarStyle: "black-translucent" },
  viewport: "width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;510;600;700&display=swap" rel="stylesheet" />
      </head>
      <body style={{ margin: 0, fontFamily: "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif", WebkitFontSmoothing: "antialiased", background: "#08090a", color: "#f7f8f8", minHeight: "100vh" }}>
        {children}
        <script dangerouslySetInnerHTML={{
          __html: `
            if ('serviceWorker' in navigator) {
              window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js');
              });
            }
          `,
        }} />
      </body>
    </html>
  );
}