'use client';

import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useMediaStream } from '../hooks/useMediaStream';
import WebcamView from '../components/WebcamView';
import AudioVisualizer from '../components/AudioVisualizer';
import ControlButtons from '../components/ControlButtons';
import ConversationLog from '../components/ConversationLog';
import MediaControls from '../components/MediaControls';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'model' | 'system';
}

export default function TalkToDoctor() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isListening, setIsListening] = useState(false);

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

  const addMessage = useCallback((text: string, sender: 'user' | 'model' | 'system') => {
    setMessages((prev) => {
      if (sender === 'model' && prev.length > 0 && prev[prev.length - 1].sender === 'model') {
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
            addMessage(message.text, 'model');
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
      // Request both video and audio for Talk to Doctor
      await startStream(
        (blob) => {
          if (isConnected) {
            send(blob);
          }
        },
        {
          video: true, // Explicitly request video
          audio: true,
        }
      );

      send(JSON.stringify({ type: 'start' }));
      setIsListening(true);
      addMessage('Recording started...', 'system');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to start recording';
      addMessage(`Error: ${message}`, 'system');
      alert(message);
    }
  }, [startStream, send, isConnected, addMessage]);

  const handleStop = useCallback(() => {
    stopStream();
    send(JSON.stringify({ type: 'stop' }));
    setIsListening(false);
  }, [stopStream, send]);

  const handleTestAudio = useCallback(() => {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(440, audioContext.currentTime);
    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);

    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.5);

    addMessage('Playing test beep...', 'system');
  }, [addMessage]);

  return (
    <div className="min-h-screen bg-dark-950 flex flex-col">
      {/* Header with Connection Status */}
      <header className="border-b border-dark-800 bg-dark-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">Talk to Doctor</h1>
            <p className="text-sm text-gray-400">Real-time consultation with healthcare professionals</p>
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
          {/* Webcam View */}
          <div className="flex-1 min-h-[400px]">
            <WebcamView stream={stream} isListening={isListening} />
          </div>

          {/* Media Controls */}
          <div className="flex items-center justify-center">
            <MediaControls
              webcamEnabled={webcamEnabled}
              microphoneEnabled={microphoneEnabled}
              onToggleWebcam={toggleWebcam}
              onToggleMicrophone={toggleMicrophone}
              disabled={!isRecording}
            />
          </div>

          {/* Audio Visualizer */}
          <AudioVisualizer stream={stream} isRecording={isRecording} microphoneEnabled={microphoneEnabled} />

          {/* Control Buttons */}
          <ControlButtons
            isConnected={isConnected}
            isRecording={isRecording}
            onStart={handleStart}
            onStop={handleStop}
            onTestAudio={handleTestAudio}
          />
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

