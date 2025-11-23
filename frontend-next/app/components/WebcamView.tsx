'use client';

import { useEffect, useRef, useState } from 'react';

interface WebcamViewProps {
  stream: MediaStream | null;
  isListening: boolean;
}

export default function WebcamView({ stream, isListening }: WebcamViewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [showPlaceholder, setShowPlaceholder] = useState(true);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    console.log('WebcamView effect - stream changed:', {
      hasStream: !!stream,
      streamId: stream?.id,
    });

    if (stream) {
      const videoTracks = stream.getVideoTracks();
      console.log('Video tracks:', {
        count: videoTracks.length,
        tracks: videoTracks.map(t => ({
          id: t.id,
          enabled: t.enabled,
          readyState: t.readyState,
          label: t.label,
        })),
      });

      if (videoTracks.length > 0) {
        const videoTrack = videoTracks[0];
        
        // Set the stream to the video element
        if (video.srcObject !== stream) {
          console.log('Setting video srcObject to stream');
          video.srcObject = stream;
        }

        // Check if track is enabled
        setShowPlaceholder(!videoTrack.enabled || videoTrack.readyState === 'ended');

        // Try to play the video
        const playVideo = async () => {
          try {
            await video.play();
            console.log('Video is playing');
          } catch (err) {
            console.error('Error playing video:', err);
          }
        };

        playVideo();

        // Listen for track state changes
        const handleTrackStateChange = () => {
          console.log('Track state changed:', {
            enabled: videoTrack.enabled,
            readyState: videoTrack.readyState,
          });
          setShowPlaceholder(!videoTrack.enabled || videoTrack.readyState === 'ended');
          
          if (videoTrack.enabled && videoTrack.readyState === 'live') {
            playVideo();
          }
        };

        videoTrack.addEventListener('ended', handleTrackStateChange);
        videoTrack.addEventListener('mute', handleTrackStateChange);
        videoTrack.addEventListener('unmute', handleTrackStateChange);

        // Also poll for enabled state changes
        const checkInterval = setInterval(() => {
          const currentEnabled = videoTrack.enabled;
          const currentReadyState = videoTrack.readyState;
          const shouldShowPlaceholder = !currentEnabled || currentReadyState === 'ended';
          
          if (shouldShowPlaceholder !== showPlaceholder) {
            console.log('Placeholder state changed via polling:', shouldShowPlaceholder);
            setShowPlaceholder(shouldShowPlaceholder);
          }

          // If video should be playing but isn't, try to play
          if (currentEnabled && currentReadyState === 'live' && video.paused) {
            playVideo();
          }
        }, 200);

        return () => {
          clearInterval(checkInterval);
          videoTrack.removeEventListener('ended', handleTrackStateChange);
          videoTrack.removeEventListener('mute', handleTrackStateChange);
          videoTrack.removeEventListener('unmute', handleTrackStateChange);
        };
      } else {
        console.log('No video tracks in stream');
        setShowPlaceholder(true);
        if (video.srcObject) {
          video.srcObject = null;
        }
      }
    } else {
      console.log('No stream provided');
      setShowPlaceholder(true);
      if (video.srcObject) {
        video.srcObject = null;
      }
    }
  }, [stream, showPlaceholder]);

  return (
    <div className="relative w-full h-full bg-black rounded-xl overflow-hidden border border-dark-800 shadow-2xl">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-full object-cover"
        style={{ transform: 'scaleX(-1)' }}
        onLoadedMetadata={() => {
          console.log('Video metadata loaded');
          if (videoRef.current) {
            videoRef.current.play().catch(console.error);
          }
        }}
        onCanPlay={() => {
          console.log('Video can play');
          if (videoRef.current) {
            videoRef.current.play().catch(console.error);
          }
        }}
        onPlay={() => {
          console.log('Video is now playing');
          setShowPlaceholder(false);
        }}
        onPause={() => {
          console.log('Video paused');
        }}
        onError={(e) => {
          console.error('Video element error:', e);
        }}
      />
      {isListening && !showPlaceholder && (
        <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-3 py-2 rounded-full flex items-center gap-2 border border-dark-700 z-20">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
          <span className="text-sm font-medium text-white">Listening...</span>
        </div>
      )}
      {showPlaceholder && (
        <div className="absolute inset-0 flex items-center justify-center bg-dark-900 z-10">
          <div className="text-center">
            <svg
              className="w-16 h-16 mx-auto mb-4 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
            <p className="text-gray-500 text-sm">
              {!stream ? 'Webcam will appear here' : 'Webcam is disabled'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
