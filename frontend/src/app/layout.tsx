import "./globals.css";
import EnvConfigChecker from "@/components/EnvConfigChecker";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <title>AIDrama Studio</title>
        <meta name="description" content="Jellyfish-oriented industrial AI Film Engine" />
      </head>
      <body className="font-sans bg-background text-foreground antialiased">
        <EnvConfigChecker />
        {children}
      </body>
    </html>
  );
}
