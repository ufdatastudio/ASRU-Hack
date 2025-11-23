'use client';

interface ControlButtonsProps {
  isConnected: boolean;
  isRecording: boolean;
  onStart: () => void;
  onStop: () => void;
  onTestAudio: () => void;
}

export default function ControlButtons({
  isConnected,
  isRecording,
  onStart,
  onStop,
  onTestAudio,
}: ControlButtonsProps) {
  return (
    <div className="flex items-center justify-center gap-4">
      <button
        onClick={onStart}
        disabled={!isConnected || isRecording}
        className="flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-dark-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors shadow-lg disabled:shadow-none"
      >
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
          />
        </svg>
        Start Conversation
      </button>

      <button
        onClick={onStop}
        disabled={!isRecording}
        className="flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-dark-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors shadow-lg disabled:shadow-none"
      >
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
          />
        </svg>
        Stop
      </button>

      <button
        onClick={onTestAudio}
        className="px-4 py-3 bg-dark-800 hover:bg-dark-700 text-gray-300 hover:text-white font-medium rounded-lg transition-colors border border-dark-700"
      >
        Test Audio
      </button>
    </div>
  );
}

