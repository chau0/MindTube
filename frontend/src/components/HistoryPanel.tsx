'use client';

import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { X, Clock, Trash2, ExternalLink } from 'lucide-react';
import { useProcessingStore } from '@/lib/store';
import { utils } from '@/lib/api';

interface HistoryPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HistoryPanel({ isOpen, onClose }: HistoryPanelProps) {
  const { history, removeFromHistory } = useProcessingStore();

  const handleOpenResult = (jobId: string) => {
    // TODO: Implement navigation to result page
    window.open(`/r/${jobId}`, '_blank');
  };

  const handleDelete = (jobId: string) => {
    removeFromHistory(jobId);
  };

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-in-out duration-500"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in-out duration-500"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
              <Transition.Child
                as={Fragment}
                enter="transform transition ease-in-out duration-500 sm:duration-700"
                enterFrom="translate-x-full"
                enterTo="translate-x-0"
                leave="transform transition ease-in-out duration-500 sm:duration-700"
                leaveFrom="translate-x-0"
                leaveTo="translate-x-full"
              >
                <Dialog.Panel className="pointer-events-auto w-screen max-w-md">
                  <div className="flex h-full flex-col overflow-y-scroll bg-white shadow-xl">
                    {/* Header */}
                    <div className="bg-primary-600 px-4 py-6 sm:px-6">
                      <div className="flex items-center justify-between">
                        <Dialog.Title className="text-base font-semibold leading-6 text-white">
                          Processing History
                        </Dialog.Title>
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
                      <div className="mt-1">
                        <p className="text-sm text-primary-200">
                          {history.length} video{history.length !== 1 ? 's' : ''} processed
                        </p>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="relative flex-1 px-4 py-6 sm:px-6">
                      {history.length === 0 ? (
                        <div className="text-center py-12">
                          <Clock className="mx-auto h-12 w-12 text-gray-400" />
                          <h3 className="mt-2 text-sm font-medium text-gray-900">No history yet</h3>
                          <p className="mt-1 text-sm text-gray-500">
                            Process your first video to see it here.
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {history.map((item) => (
                            <div
                              key={item.job_id}
                              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                  <h4 className="text-sm font-medium text-gray-900 truncate">
                                    {item.video_metadata.title}
                                  </h4>
                                  <p className="text-sm text-gray-500 truncate">
                                    {item.video_metadata.channel_name}
                                  </p>
                                  <div className="mt-2 flex items-center text-xs text-gray-400 space-x-4">
                                    <span>{utils.formatDuration(item.video_metadata.duration_seconds)}</span>
                                    <span>{new Date(item.created_at).toLocaleDateString()}</span>
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                      item.status === 'completed' 
                                        ? 'bg-green-100 text-green-800'
                                        : item.status === 'failed'
                                        ? 'bg-red-100 text-red-800'
                                        : 'bg-yellow-100 text-yellow-800'
                                    }`}>
                                      {item.status}
                                    </span>
                                  </div>
                                </div>
                                <div className="flex items-center space-x-2 ml-4">
                                  {item.status === 'completed' && (
                                    <button
                                      onClick={() => handleOpenResult(item.job_id)}
                                      className="p-1 text-gray-400 hover:text-primary-600"
                                      title="Open result"
                                    >
                                      <ExternalLink className="w-4 h-4" />
                                    </button>
                                  )}
                                  <button
                                    onClick={() => handleDelete(item.job_id)}
                                    className="p-1 text-gray-400 hover:text-red-600"
                                    title="Delete from history"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}