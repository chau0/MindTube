'use client';

import { Fragment } from 'react';
import { X, Save } from 'lucide-react';
import { useProcessingStore } from '@/lib/store';
import toast from 'react-hot-toast';

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
  const { settings, updateSettings } = useProcessingStore();

  const handleSave = () => {
    toast.success('Settings saved!');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />
      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
            <div className="pointer-events-auto w-screen max-w-md transform transition-transform duration-300 translate-x-0">
                  <div className="flex h-full flex-col overflow-y-scroll bg-white shadow-xl">
                    {/* Header */}
                    <div className="bg-primary-600 px-4 py-6 sm:px-6">
                      <div className="flex items-center justify-between">
                        <h2 className="text-base font-semibold leading-6 text-white">
                          Settings
                        </h2>
                        <div className="ml-3 flex h-7 items-center">
                          <button
                            type="button"
                            className="rounded-md bg-primary-600 text-primary-200 hover:text-white focus:outline-none focus:ring-2 focus:ring-white"
                            onClick={onClose}
                          >
                            <span className="sr-only">Close panel</span>
                            <X className="h-6 w-6" />
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="relative flex-1 px-4 py-6 sm:px-6">
                      <div className="space-y-6">
                        {/* Processing Settings */}
                        <div>
                          <h3 className="text-lg font-medium text-gray-900 mb-4">Processing</h3>
                          
                          <div className="space-y-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <label className="text-sm font-medium text-gray-700">
                                  Enable ASR Fallback
                                </label>
                                <p className="text-xs text-gray-500">
                                  Use speech-to-text when captions are unavailable
                                </p>
                              </div>
                              <input
                                type="checkbox"
                                checked={settings.enableAsr}
                                onChange={(e) => updateSettings({ enableAsr: e.target.checked })}
                                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                              />
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Preferred Language
                              </label>
                              <select
                                value={settings.preferredLanguage}
                                onChange={(e) => updateSettings({ preferredLanguage: e.target.value })}
                                className="input-primary"
                              >
                                <option value="en">English</option>
                                <option value="ja">Japanese</option>
                                <option value="auto">Auto-detect</option>
                              </select>
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Max Video Duration (minutes)
                              </label>
                              <input
                                type="number"
                                min="1"
                                max="180"
                                value={settings.maxDurationMinutes}
                                onChange={(e) => updateSettings({ maxDurationMinutes: parseInt(e.target.value) })}
                                className="input-primary"
                              />
                              <p className="text-xs text-gray-500 mt-1">
                                Videos longer than this will be rejected
                              </p>
                            </div>
                          </div>
                        </div>

                        {/* Export Settings */}
                        <div>
                          <h3 className="text-lg font-medium text-gray-900 mb-4">Export</h3>
                          
                          <div className="space-y-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <label className="text-sm font-medium text-gray-700">
                                  Include Transcript
                                </label>
                                <p className="text-xs text-gray-500">
                                  Include full transcript in exports
                                </p>
                              </div>
                              <input
                                type="checkbox"
                                checked={settings.includeTranscript}
                                onChange={(e) => updateSettings({ includeTranscript: e.target.checked })}
                                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                              />
                            </div>

                            <div className="flex items-center justify-between">
                              <div>
                                <label className="text-sm font-medium text-gray-700">
                                  Auto Download
                                </label>
                                <p className="text-xs text-gray-500">
                                  Automatically download results when complete
                                </p>
                              </div>
                              <input
                                type="checkbox"
                                checked={settings.autoDownload}
                                onChange={(e) => updateSettings({ autoDownload: e.target.checked })}
                                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                              />
                            </div>
                          </div>
                        </div>

                        {/* About */}
                        <div>
                          <h3 className="text-lg font-medium text-gray-900 mb-4">About</h3>
                          <div className="text-sm text-gray-600 space-y-2">
                            <p><strong>Version:</strong> 0.1.0 (MVP)</p>
                            <p><strong>Status:</strong> Development</p>
                            <p><strong>API:</strong> {process.env.NEXT_PUBLIC_API_BASE}</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Footer */}
                    <div className="border-t border-gray-200 px-4 py-4 sm:px-6">
                      <button
                        onClick={handleSave}
                        className="btn-primary w-full"
                      >
                        <Save className="w-4 h-4 mr-2" />
                        Save Settings
                      </button>
                    </div>
                  </div>
                </div>
            </div>
          </div>
        </div>
    </div>
  );
}