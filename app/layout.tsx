import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"

const geist = Geist({ subsets: ["latin"] })
const geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = { title: "Nagrik Seva | Public grievance redressal", description: "Submit, route, and track civic complaints with your local department in your language.", generator: "Nagrik Seva" }

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en" className="bg-background"><body className={`${geist.className} antialiased`}><div className="min-h-screen">{children}</div><Analytics /></body></html> }
