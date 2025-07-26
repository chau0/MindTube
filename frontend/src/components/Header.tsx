'use client';

import { useState } from 'react';
import { Settings, History, Github } from 'lucide-react';
import { HistoryPanel } from './HistoryPanel';
import { SettingsPanel } from './SettingsPanel';

export function Header() {
  const [showHistory, setShowHistory] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  return (
    <>
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-primary-600">MindTube</h1>
              </div>
              <div className="hidden md:block ml-4">
                <span className="text-sm text-gray-500">AI-Powered YouTube Summarizer</span>
              </div>
            </div>

            {/* Navigation */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowHistory(true)}
                className="btn-ghost"
                title="View History"
              >
                <History className="w-5 h-5" />
                <span className="hidden sm:inline ml-2">History</span>
              </button>

              <button
                onClick={() => setShowSettings(true)}
                className="btn-ghost"
                title="Settings"
              >
                <Settings className="w-5 h-5" />
                <span className="hidden sm:inline ml-2">Settings</span>
              </button>

              <a
                href="https://github.com/yourusername/mindtube"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-ghost"
                title="View on GitHub"
              >
                <Github className="w-5 h-5" />
                <span className="hidden sm:inline ml-2">GitHub</span>
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* History Panel */}
      <HistoryPanel 
        isOpen={showHistory} 
        onClose={() => setShowHistory(false)} 
      />

      {/* Settings Panel */}
      <SettingsPanel 
        isOpen={showSettings} 
        onClose={() => setShowSettings(false)} 
      />
    </>
  );
}