// MindTube Frontend Types

export interface VideoMetadata {
  video_id: string;
  title: string;
  channel_name: string;
  duration_seconds: number;
  view_count?: number;
  published_at?: string;
  description?: string;
  language?: string;
  has_captions: boolean;
}

export interface TranscriptSegment {
  start_ms: number;
  end_ms: number;
  text: string;
  confidence?: number;
}

export interface SummarySection {
  content: string;
  timestamp_ms?: number;
  youtube_link?: string;
}

export interface ProcessingResult {
  job_id: string;
  video_metadata: VideoMetadata;
  short_summary: string[];
  detailed_summary: SummarySection[];
  key_ideas: SummarySection[];
  actionable_takeaways: SummarySection[];
  transcript: TranscriptSegment[];
  processing_stats: {
    total_duration_seconds: number;
    tokens_used: number;
    cost_usd: number;
  };
  created_at: string;
  completed_at?: string;
}

export interface ProcessingProgress {
  status: JobStatus;
  progress_percent: number;
  current_step: string;
  estimated_completion_seconds?: number;
  partial_results?: Partial<ProcessingResult>;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  progress: ProcessingProgress;
  result?: ProcessingResult;
  error?: string;
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  message: string;
  estimated_completion_seconds?: number;
}

export interface VideoIngestRequest {
  url: string;
  enable_asr?: boolean;
  language?: string;
  chunk_size?: number;
}

export type JobStatus = 
  | 'pending'
  | 'fetching_metadata'
  | 'fetching_transcript'
  | 'chunking'
  | 'mapping'
  | 'reducing'
  | 'finalizing'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface HistoryItem {
  job_id: string;
  video_metadata: VideoMetadata;
  created_at: string;
  completed_at?: string;
  status: JobStatus;
}

export interface AppSettings {
  enableAsr: boolean;
  preferredLanguage: string;
  maxDurationMinutes: number;
  includeTranscript: boolean;
  autoDownload: boolean;
}

// UI Component Props
export interface TabItem {
  id: string;
  label: string;
  count?: number;
  content: React.ReactNode;
}

export interface ProgressStep {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  error?: {
    message: string;
    code?: string;
    details?: any;
  };
}

// Error Types
export interface AppError {
  message: string;
  code?: string;
  details?: any;
  timestamp: string;
}

// Store Types
export interface ProcessingStore {
  currentJob: {
    jobId: string;
    status: JobStatus;
    progress: ProcessingProgress;
    result?: ProcessingResult;
    error?: string;
  } | null;
  history: HistoryItem[];
  settings: AppSettings;
  isProcessing: boolean;
  
  // Actions
  startProcessing: (request: VideoIngestRequest) => Promise<void>;
  pollProgress: (jobId: string) => void;
  updateProgress: (jobId: string, progress: ProcessingProgress) => void;
  setResult: (jobId: string, result: ProcessingResult) => void;
  setError: (jobId: string, error: string) => void;
  clearCurrentJob: () => void;
  addToHistory: (item: HistoryItem) => void;
  removeFromHistory: (jobId: string) => void;
  updateSettings: (settings: Partial<AppSettings>) => void;
}