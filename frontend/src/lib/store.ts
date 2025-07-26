'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ProcessingStore, VideoIngestRequest, HistoryItem, AppSettings } from '@/types';
import { apiClient } from './api';
import toast from 'react-hot-toast';

const defaultSettings: AppSettings = {
  enableAsr: false,
  preferredLanguage: 'en',
  maxDurationMinutes: 90,
  includeTranscript: true,
  autoDownload: false,
};

export const useProcessingStore = create<ProcessingStore>()(
  persist(
    (set, get) => ({
      currentJob: null,
      history: [],
      settings: defaultSettings,
      isProcessing: false,

      startProcessing: async (request: VideoIngestRequest) => {
        try {
          set({ isProcessing: true });
          
          const response = await apiClient.ingestVideo(request);
          
          set({
            currentJob: {
              jobId: response.job_id,
              status: response.status,
              progress: {
                status: response.status,
                progress_percent: 0,
                current_step: 'Initializing...',
                estimated_completion_seconds: response.estimated_completion_seconds,
              },
            },
          });

          // Start polling for progress
          get().pollProgress(response.job_id);
          
          toast.success('Processing started!');
        } catch (error) {
          set({ isProcessing: false });
          const errorMessage = error instanceof Error ? error.message : 'Failed to start processing';
          toast.error(errorMessage);
          throw error;
        }
      },

      pollProgress: async (jobId: string) => {
        const pollInterval = setInterval(async () => {
          try {
            const status = await apiClient.getJobStatus(jobId);
            
            set((state) => ({
              currentJob: state.currentJob ? {
                ...state.currentJob,
                status: status.status,
                progress: status.progress,
                result: status.result,
                error: status.error,
              } : null,
            }));

            // Stop polling if job is complete or failed
            if (['completed', 'failed', 'cancelled'].includes(status.status)) {
              clearInterval(pollInterval);
              set({ isProcessing: false });
              
              if (status.status === 'completed' && status.result) {
                // Add to history
                get().addToHistory({
                  job_id: jobId,
                  video_metadata: status.result.video_metadata,
                  created_at: status.result.created_at,
                  completed_at: status.result.completed_at,
                  status: status.status,
                });
                
                toast.success('Processing completed!');
              } else if (status.status === 'failed') {
                toast.error(status.error || 'Processing failed');
              }
            }
          } catch (error) {
            clearInterval(pollInterval);
            set({ isProcessing: false });
            const errorMessage = error instanceof Error ? error.message : 'Failed to get status';
            get().setError(jobId, errorMessage);
            toast.error(errorMessage);
          }
        }, 2000); // Poll every 2 seconds
      },

      updateProgress: (jobId: string, progress) => {
        set((state) => ({
          currentJob: state.currentJob?.jobId === jobId ? {
            ...state.currentJob,
            progress,
            status: progress.status,
          } : state.currentJob,
        }));
      },

      setResult: (jobId: string, result) => {
        set((state) => ({
          currentJob: state.currentJob?.jobId === jobId ? {
            ...state.currentJob,
            result,
            status: 'completed',
          } : state.currentJob,
          isProcessing: false,
        }));
      },

      setError: (jobId: string, error) => {
        set((state) => ({
          currentJob: state.currentJob?.jobId === jobId ? {
            ...state.currentJob,
            error,
            status: 'failed',
          } : state.currentJob,
          isProcessing: false,
        }));
      },

      clearCurrentJob: () => {
        set({ currentJob: null, isProcessing: false });
      },

      addToHistory: (item: HistoryItem) => {
        set((state) => ({
          history: [item, ...state.history.filter(h => h.job_id !== item.job_id)].slice(0, 20),
        }));
      },

      removeFromHistory: (jobId: string) => {
        set((state) => ({
          history: state.history.filter(h => h.job_id !== jobId),
        }));
      },

      updateSettings: (newSettings: Partial<AppSettings>) => {
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        }));
      },
    }),
    {
      name: 'mindtube-store',
      partialize: (state) => ({
        history: state.history,
        settings: state.settings,
      }),
    }
  )
);