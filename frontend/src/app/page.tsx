'use client';

import { useState } from 'react';
import { VideoUrlInput } from '@/components/VideoUrlInput';
import { ProcessingProgress } from '@/components/ProcessingProgress';
import { ResultsTabs } from '@/components/ResultsTabs';
import { Header } from '@/components/Header';
import { useProcessingStore } from '@/lib/store';

export default function HomePage() {
  const { currentJob, isProcessing } = useProcessingStore();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Hero Section */}
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl">
              Transform YouTube Videos into
              <span className="text-primary-600"> Actionable Insights</span>
            </h1>
            <p className="mt-4 text-xl text-gray-600 max-w-2xl mx-auto">
              Get AI-powered summaries, key ideas, and timestamped takeaways from any YouTube video in seconds.
            </p>
          </div>

          {/* URL Input */}
          <VideoUrlInput />

          {/* Processing Progress */}
          {isProcessing && currentJob && (
            <ProcessingProgress jobId={currentJob.jobId} />
          )}

          {/* Results */}
          {currentJob?.result && (
            <ResultsTabs result={currentJob.result} />
          )}

          {/* Features Preview (shown when no active job) */}
          {!currentJob && (
            <div className="grid md:grid-cols-3 gap-6 mt-12">
              <div className="card">
                <div className="card-body text-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Lightning Fast</h3>
                  <p className="text-gray-600">Get summaries in under 15 seconds for most videos with captions.</p>
                </div>
              </div>

              <div className="card">
                <div className="card-body text-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Smart Summaries</h3>
                  <p className="text-gray-600">AI extracts key ideas and actionable takeaways with timestamp links.</p>
                </div>
              </div>

              <div className="card">
                <div className="card-body text-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Export Ready</h3>
                  <p className="text-gray-600">Download as Markdown or copy to clipboard for your notes.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}