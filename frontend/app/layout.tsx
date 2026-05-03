import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'BI AI Engine - Stock Intelligence Dashboard',
  description: 'Business Intelligence dashboard with AI-powered stock analysis using FinBERT sentiment and market data.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <main className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
          {children}
        </main>
      </body>
    </html>
  )
}

