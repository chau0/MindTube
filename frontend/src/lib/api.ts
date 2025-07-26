'use client';

import axios, { AxiosResponse } from 'axios';
import { 
  VideoIngestRequest, 
  JobResponse, 
  JobStatusResponse, 
  ProcessingResult 
} from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    
    // Transform error for consistent handling
    const errorMessage = error.response?.data?.message || 
                         error.response?.data?.detail || 
                         error.message || 
                         'An unexpected error occurred';
    
    throw new Error(errorMessage);
  }
);

export const apiClient = {
  // Ingest a video for processing
  async ingestVideo(request: VideoIngestRequest): Promise<JobResponse> {
    const response = await api.post<JobResponse>('/ingest', request);
    return response.data;
  },

  // Get job status and progress
  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    const response = await api.get<JobStatusResponse>(`/status/${jobId}`);
    return response.data;
  },

  // Get completed job result
  async getJobResult(jobId: string): Promise<ProcessingResult> {
    const response = await api.get<ProcessingResult>(`/result/${jobId}`);
    return response.data;
  },

  // Cancel a running job
  async cancelJob(jobId: string): Promise<{ message: string }> {
    const response = await api.delete(`/status/${jobId}`);
    return response.data;
  },

  // Export result as markdown
  async exportMarkdown(jobId: string): Promise<string> {
    const response = await api.get(`/export/${jobId}/markdown`, {
      responseType: 'text',
    });
    return response.data;
  },

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await api.get('/health');
    return response.data;
  },
};

// Utility functions
export const utils = {
  // Validate YouTube URL
  isValidYouTubeUrl(url: string): boolean {
    const patterns = [
      /^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})/,
      /^https?:\/\/youtu\.be\/([a-zA-Z0-9_-]{11})/,
      /^https?:\/\/(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
    ];
    
    return patterns.some(pattern => pattern.test(url));
  },

  // Extract video ID from YouTube URL
  extractVideoId(url: string): string | null {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) return match[1];
    }
    
    return null;
  },

  // Format duration from seconds to MM:SS
  formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  },

  // Format timestamp from milliseconds to MM:SS
  formatTimestamp(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    return this.formatDuration(seconds);
  },

  // Create YouTube timestamp URL
  createTimestampUrl(baseUrl: string, timestampMs: number): string {
    const seconds = Math.floor(timestampMs / 1000);
    const url = new URL(baseUrl);
    url.searchParams.set('t', `${seconds}s`);
    return url.toString();
  },

  // Download text as file
  downloadAsFile(content: string, filename: string, mimeType = 'text/plain'): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },

  // Copy text to clipboard
  async copyToClipboard(text: string): Promise<boolean> {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      return false;
    }
  },
};