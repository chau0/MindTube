import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Toaster } from 'react-hot-toast';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'MindTube - AI-Powered YouTube Summarizer',
  description: 'Transform long YouTube videos into concise, actionable insights with timestamped summaries, key ideas, and takeaways.',
  keywords: ['YouTube', 'AI', 'summarization', 'video analysis', 'learning'],
  authors: [{ name: 'MindTube Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
  openGraph: {
    title: 'MindTube - AI-Powered YouTube Summarizer',
    description: 'Transform long YouTube videos into concise, actionable insights',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'MindTube - AI-Powered YouTube Summarizer',
    description: 'Transform long YouTube videos into concise, actionable insights',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-gray-50 antialiased`}>
        <div className="min-h-full">
          {children}
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#22c55e',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </body>
    </html>
  );
}