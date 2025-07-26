'use client';

import { useState } from 'react';
import { Copy, Download, ExternalLink } from 'lucide-react';
import { ProcessingResult } from '@/types';
import { utils, apiClient } from '@/lib/api';
import toast from 'react-hot-toast';

interface ResultsTabsProps {
  result: ProcessingResult;
}

export function ResultsTabs({ result }: ResultsTabsProps) {
  const [activeTab, setActiveTab] = useState('summary');
  const [isExporting, setIsExporting] = useState(false);

  const tabs = [
    { id: 'summary', label: 'Summary', count: result.short_summary.length },
    { id: 'detailed', label: 'Detailed', count: result.detailed_summary.length },
    { id: 'ideas', label: 'Key Ideas', count: result.key_ideas.length },
    { id: 'takeaways', label: 'Takeaways', count: result.actionable_takeaways.length },
    { id: 'transcript', label: 'Transcript', count: result.transcript.length },
  ];

  const handleCopy = async (content: string) => {
    const success = await utils.copyToClipboard(content);
    if (success) {
      toast.success('Copied to clipboard!');
    } else {
      toast.error('Failed to copy to clipboard');
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const markdown = await apiClient.exportMarkdown(result.job_id);
      const filename = `${result.video_metadata.title.replace(/[^a-z0-9]/gi, '_')}_MindTube.md`;
      utils.downloadAsFile(markdown, filename, 'text/markdown');
      toast.success('Markdown exported successfully!');
    } catch (error) {
      toast.error('Failed to export markdown');
    } finally {
      setIsExporting(false);
    }
  };

  const TimestampChip = ({ timestampMs, youtubeLink }: { timestampMs?: number; youtubeLink?: string }) => {
    if (!timestampMs || !youtubeLink) return null;
    
    return (
      <button
        onClick={() => window.open(youtubeLink, '_blank')}
        className="timestamp-chip ml-2"
        title="Jump to timestamp in video"
      >
        {utils.formatTimestamp(timestampMs)}
        <ExternalLink className="w-3 h-3 ml-1" />
      </button>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'summary':
        return (
          <div className="space-y-3">
            {result.short_summary.map((line, index) => (
              <div key={index} className="flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                <span className="text-gray-700">{line}</span>
              </div>
            ))}
          </div>
        );

      case 'detailed':
        return (
          <div className="space-y-4">
            {result.detailed_summary.map((item, index) => (
              <div key={index} className="border-l-4 border-primary-200 pl-4">
                <p className="text-gray-700 leading-relaxed">{item.content}</p>
                <TimestampChip timestampMs={item.timestamp_ms} youtubeLink={item.youtube_link} />
              </div>
            ))}
          </div>
        );

      case 'ideas':
        return (
          <div className="space-y-3">
            {result.key_ideas.map((idea, index) => (
              <div key={index} className="flex items-start">
                <span className="text-yellow-500 mr-2">💡</span>
                <div className="flex-1">
                  <span className="text-gray-700">{idea.content}</span>
                  <TimestampChip timestampMs={idea.timestamp_ms} youtubeLink={idea.youtube_link} />
                </div>
              </div>
            ))}
          </div>
        );

      case 'takeaways':
        return (
          <div className="space-y-3">
            {result.actionable_takeaways.map((takeaway, index) => (
              <div key={index} className="flex items-start">
                <span className="text-green-500 mr-2">🎯</span>
                <div className="flex-1">
                  <span className="text-gray-700">{takeaway.content}</span>
                  <TimestampChip timestampMs={takeaway.timestamp_ms} youtubeLink={takeaway.youtube_link} />
                </div>
              </div>
            ))}
          </div>
        );

      case 'transcript':
        return (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {result.transcript.map((segment, index) => (
              <div key={index} className="flex items-start text-sm">
                <span className="text-gray-400 mr-3 font-mono text-xs">
                  {utils.formatTimestamp(segment.start_ms)}
                </span>
                <span className="text-gray-700">{segment.text}</span>
              </div>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  const getTabContent = () => {
    switch (activeTab) {
      case 'summary':
        return result.short_summary.join('\n• ');
      case 'detailed':
        return result.detailed_summary.map(item => item.content).join('\n\n');
      case 'ideas':
        return result.key_ideas.map(item => item.content).join('\n• ');
      case 'takeaways':
        return result.actionable_takeaways.map(item => item.content).join('\n• ');
      case 'transcript':
        return result.transcript.map(segment => 
          `[${utils.formatTimestamp(segment.start_ms)}] ${segment.text}`
        ).join('\n');
      default:
        return '';
    }
  };

  return (
    <div className="card">
      {/* Video Info Header */}
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{result.video_metadata.title}</h2>
            <p className="text-sm text-gray-600 mt-1">
              {result.video_metadata.channel_name} • {utils.formatDuration(result.video_metadata.duration_seconds)}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleCopy(getTabContent())}
              className="btn-secondary"
              title="Copy current tab content"
            >
              <Copy className="w-4 h-4 mr-2" />
              Copy
            </button>
            <button
              onClick={handleExport}
              disabled={isExporting}
              className="btn-primary"
              title="Export as Markdown"
            >
              {isExporting ? (
                <div className="spinner w-4 h-4 mr-2" />
              ) : (
                <Download className="w-4 h-4 mr-2" />
              )}
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="tab-list px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`tab-button ${
                activeTab === tab.id ? 'tab-button-active' : 'tab-button-inactive'
              }`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="card-body">
        {renderContent()}
      </div>

      {/* Processing Stats */}
      <div className="card-footer">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div>
            Processed in {result.processing_stats.total_duration_seconds}s • 
            {result.processing_stats.tokens_used} tokens • 
            ${result.processing_stats.cost_usd.toFixed(3)}
          </div>
          <div>
            {new Date(result.completed_at || result.created_at).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
}