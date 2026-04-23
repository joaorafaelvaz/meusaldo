import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MeuSaldo | Inteligência Financeira",
  description: "Acompanhe seus gastos via WhatsApp",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pt-BR"
      className={`${outfit.variable} font-sans h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-black">{children}</body>
    </html>
  );
}
