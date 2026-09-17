import type { Metadata } from "next";
import type { ReactNode } from "react";

import {
  Geist,
  Geist_Mono,
} from "next/font/google";

import AppAuthGate from "../components/AppAuthGate";

import "./globals.css";


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});


const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});


export const metadata: Metadata = {
  title: "MissionGuard AI",
  description:
    "Educational space-weather risk intelligence and mission-readiness prototype.",
};


export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <AppAuthGate>
          {children}
        </AppAuthGate>
      </body>
    </html>
  );
}
