'use client';

import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useMediaStream } from '../hooks/useMediaStream';
import WebcamView from '../components/WebcamView';
import AudioVisualizer from '../components/AudioVisualizer';
import ConversationLog from '../components/ConversationLog';
import MediaControls from '../components/MediaControls';
import ModelSelector from '../components/ModelSelector';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai' | 'system';
}

export default function TalkToAI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [webcamOn, setWebcamOn] = useState(false); // Option to start without webcam
  const [selectedModel, setSelectedModel] = useState('audio-flamingo-3');

  // WebSocket connection
  const wsProtocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
  const wsPort = '8000';
  const wsUrl = `${wsProtocol}//${wsHost}:${wsPort}/ws/audio`;

  const { isConnected, send, onMessage } = useWebSocket(wsUrl);
  const { 
    stream, 
    isRecording, 
    webcamEnabled,
    microphoneEnabled,
    startStream, 
    stopStream,
    toggleWebcam,
    toggleMicrophone,
  } = useMediaStream();

  const addMessage = useCallback((text: string, sender: 'user' | 'ai' | 'system') => {
    setMessages((prev) => {
      if (sender === 'ai' && prev.length > 0 && prev[prev.length - 1].sender === 'ai') {
        return prev.map((msg, idx) =>
          idx === prev.length - 1 ? { ...msg, text } : msg
        );
      }
      return [...prev, { id: Date.now().toString(), text, sender }];
    });
  }, []);

  // Handle WebSocket messages
  useEffect(() => {
    const unsubscribe = onMessage((data) => {
      if (data instanceof Blob) {
        const url = URL.createObjectURL(data);
        const audio = new Audio(url);
        audio.play().catch((e) => console.error('Error playing audio:', e));
      } else {
        try {
          const message = JSON.parse(data as string);
          if (message.type === 'text_update') {
            addMessage(message.text, 'ai');
          }
        } catch (e) {
          console.log('Received text:', data);
        }
      }
    });
    return unsubscribe;
  }, [onMessage, addMessage]);

  const handleStart = useCallback(async () => {
    try {
      // Request media based on user's webcam preference
      await startStream(
        (blob) => {
          // Send audio data if connected
          // Microphone mute is handled at the track level
          if (isConnected) {
            send(blob);
          }
        },
        {
          video: webcamOn,
          audio: true,
        }
      );

      send(JSON.stringify({ type: 'start', model: selectedModel }));
      setIsListening(true);
      addMessage(`AI conversation started with ${selectedModel}...`, 'system');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to start conversation';
      addMessage(`Error: ${message}`, 'system');
      alert(message);
    }
  }, [startStream, send, isConnected, addMessage, microphoneEnabled, webcamOn, selectedModel]);

  const handleStop = useCallback(() => {
    stopStream();
    send(JSON.stringify({ type: 'stop' }));
    setIsListening(false);
  }, [stopStream, send]);

  const handleToggleWebcamOption = useCallback(() => {
    if (isRecording) {
      // If already recording, toggle the webcam track
      toggleWebcam();
      setWebcamOn(!webcamEnabled);
    } else {
      // If not recording, just toggle the preference for next session
      setWebcamOn(!webcamOn);
    }
  }, [isRecording, toggleWebcam, webcamEnabled, webcamOn]);

  return (
    <div className="min-h-screen bg-dark-950 flex flex-col">
      {/* Header */}
      <header className="border-b border-dark-800 bg-dark-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">Talk to AI</h1>
            <p className="text-sm text-gray-400">Have a conversation with AI using audio and optional video</p>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              } ${isConnected ? 'animate-pulse' : ''}`}
            />
            <span className="text-sm text-gray-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-6 py-6 grid grid-cols-1 lg:grid-cols-[1.2fr,0.8fr] gap-6 min-h-0">
        {/* Left Column - Media */}
        <div className="flex flex-col gap-6">
          {/* Model Selector */}
          <div className="bg-dark-900 rounded-xl p-4 border border-dark-800">
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
              disabled={isRecording}
            />
          </div>

          {/* Webcam Option Toggle */}
          <div className="bg-dark-900 rounded-xl p-4 border border-dark-800">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={isRecording ? webcamEnabled : webcamOn}
                onChange={handleToggleWebcamOption}
                className="w-5 h-5 rounded border-dark-700 bg-dark-800 text-primary-600 focus:ring-primary-600 focus:ring-2"
              />
              <span className="text-gray-300 font-medium">
                {isRecording ? 'Webcam' : 'Enable Webcam'}
              </span>
              {!isRecording && (
                <span className="text-sm text-gray-500">(Optional - audio conversation works without it)</span>
              )}
            </label>
          </div>

          {/* Webcam View - Show only if webcam is enabled and recording */}
          {isRecording && stream && webcamEnabled && (
            <div className="flex-1 min-h-[400px]">
              <WebcamView stream={stream} isListening={isListening} />
            </div>
          )}

          {/* Audio Only View - Show when webcam is off or not recording */}
          {(!isRecording || !webcamEnabled || !stream) && (
            <div className="flex-1 min-h-[400px] flex items-center justify-center bg-dark-900 rounded-xl border border-dark-800">
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-6 bg-primary-600/20 rounded-full flex items-center justify-center">
                  <svg className="w-12 h-12 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">Audio-Only Conversation</h3>
                <p className="text-gray-400">Your conversation with AI will be audio-only</p>
                <p className="text-sm text-gray-500 mt-2">Enable webcam above if you want video</p>
              </div>
            </div>
          )}

          {/* Media Controls */}
          {isRecording && (
            <div className="flex items-center justify-center">
              <MediaControls
                webcamEnabled={webcamEnabled}
                microphoneEnabled={microphoneEnabled}
                onToggleWebcam={toggleWebcam}
                onToggleMicrophone={toggleMicrophone}
                disabled={false}
              />
            </div>
          )}

          {/* Audio Visualizer */}
          {isRecording && (
            <AudioVisualizer stream={stream} isRecording={isRecording} microphoneEnabled={microphoneEnabled} />
          )}

          {/* Control Buttons */}
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={handleStart}
              disabled={!isConnected || isRecording}
              className="flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-dark-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors shadow-lg disabled:shadow-none"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
              Start AI Conversation
            </button>

            <button
              onClick={handleStop}
              disabled={!isRecording}
              className="flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-dark-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors shadow-lg disabled:shadow-none"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
              </svg>
              End Conversation
            </button>
          </div>
        </div>

        {/* Right Column - Chat */}
        <div className="flex flex-col bg-dark-900 rounded-xl border border-dark-800 shadow-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-dark-800">
            <h2 className="text-lg font-semibold text-gray-200">Conversation</h2>
          </div>
          <ConversationLog messages={messages} />
        </div>
      </main>
    </div>
  );
}

