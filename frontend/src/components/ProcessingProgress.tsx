'use client';

import { useEffect } from 'react';
import { CheckCircle, Clock, AlertCircle, X } from 'lucide-react';
import { useProcessingStore } from '@/lib/store';
import { JobStatus } from '@/types';

interface ProcessingProgressProps {
  jobId: string;
}

const statusSteps: Array<{ status: JobStatus; label: string }> = [
  { status: 'pending', label: 'Initializing' },
  { status: 'fetching_metadata', label: 'Fetching Metadata' },
  { status: 'fetching_transcript', label: 'Extracting Transcript' },
  { status: 'chunking', label: 'Chunking Content' },
  { status: 'mapping', label: 'Generating Summaries' },
  { status: 'reducing', label: 'Finalizing Results' },
  { status: 'completed', label: 'Completed' },
];

export function ProcessingProgress({ jobId }: ProcessingProgressProps) {
  const { currentJob, clearCurrentJob } = useProcessingStore();

  if (!currentJob || currentJob.jobId !== jobId) {
    return null;
  }

  const { status, progress, error } = currentJob;

  const handleCancel = () => {
    // TODO: Implement job cancellation API call
    clearCurrentJob();
  };

  const getStepStatus = (stepStatus: JobStatus) => {
    const currentIndex = statusSteps.findIndex(step => step.status === status);
    const stepIndex = statusSteps.findIndex(step => step.status === stepStatus);
    
    if (status === 'failed') return 'error';
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  const getStepIcon = (stepStatus: JobStatus) => {
    const stepState = getStepStatus(stepStatus);
    
    switch (stepState) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'active':
        return <div className="spinner w-5 h-5" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-300" />;
    }
  };

  if (status === 'failed') {
    return (
      <div className="card">
        <div className="card-body">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-red-600">Processing Failed</h3>
            <button onClick={clearCurrentJob} className="btn-ghost p-2">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <AlertCircle className="w-5 h-5 text-red-400 mt-0.5" />
              <div className="ml-3">
                <h4 className="text-sm font-medium text-red-800">Error</h4>
                <p className="text-sm text-red-700 mt-1">
                  {error || 'An unexpected error occurred during processing.'}
                </p>
              </div>
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button onClick={clearCurrentJob} className="btn-secondary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-body">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900">Processing Video</h3>
          <button
            onClick={handleCancel}
            className="btn-ghost text-red-600 hover:text-red-700 p-2"
            title="Cancel Processing"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>{progress.current_step}</span>
            <span>{progress.progress_percent}%</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${progress.progress_percent}%` }}
            />
          </div>
          {progress.estimated_completion_seconds && (
            <div className="text-xs text-gray-500 mt-1">
              Estimated completion: {progress.estimated_completion_seconds}s
            </div>
          )}
        </div>

        {/* Step Indicators */}
        <div className="space-y-3">
          {statusSteps.slice(0, -1).map((step, index) => {
            const stepState = getStepStatus(step.status);
            return (
              <div key={step.status} className="flex items-center">
                <div className="flex-shrink-0">
                  {getStepIcon(step.status)}
                </div>
                <div className="ml-3 flex-1">
                  <p className={`text-sm font-medium ${
                    stepState === 'completed' ? 'text-green-600' :
                    stepState === 'active' ? 'text-primary-600' :
                    stepState === 'error' ? 'text-red-600' :
                    'text-gray-500'
                  }`}>
                    {step.label}
                  </p>
                </div>
                {stepState === 'completed' && (
                  <div className="text-xs text-green-600">✓</div>
                )}
              </div>
            );
          })}
        </div>

        {/* Partial Results */}
        {progress.partial_results?.short_summary && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Early Preview</h4>
            <div className="bg-gray-50 rounded-md p-4">
              <div className="text-sm text-gray-700">
                {progress.partial_results.short_summary.slice(0, 2).map((line, index) => (
                  <p key={index} className="mb-1">• {line}</p>
                ))}
                {progress.partial_results.short_summary.length > 2 && (
                  <p className="text-gray-500 italic">...</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}