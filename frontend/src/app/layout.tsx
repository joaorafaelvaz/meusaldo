import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const plusJakartaSans = Plus_Jakarta_Sans({
  variable: "--font-plus-jakarta-sans",
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
      className={`${plusJakartaSans.variable} font-sans h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-black">{children}</body>
    </html>
  );
}
