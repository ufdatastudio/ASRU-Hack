import { useState, useRef, useCallback, useEffect } from 'react';

export function useMediaStream() {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [webcamEnabled, setWebcamEnabled] = useState(true);
  const [microphoneEnabled, setMicrophoneEnabled] = useState(true);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const videoTrackRef = useRef<MediaStreamTrack | null>(null);
  const audioTrackRef = useRef<MediaStreamTrack | null>(null);

  const startStream = useCallback(async (onDataAvailable?: (blob: Blob) => void, options?: { video?: boolean; audio?: boolean }) => {
    try {
      setError(null);
      // Use constraints - start simple for better compatibility
      const constraints: MediaStreamConstraints = {
        audio: options?.audio !== false,
        video: options?.video !== false,
      };
      
      // If video is requested, add some preferred settings but keep it simple
      if (options?.video !== false) {
        constraints.video = {
          width: { ideal: 1280, min: 640 },
          height: { ideal: 720, min: 480 },
          facingMode: 'user',
        };
      }
      
      console.log('Requesting media with constraints:', JSON.stringify(constraints, null, 2));
      
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('getUserMedia is not supported in this browser');
      }
      
      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      console.log('Media stream obtained successfully:', mediaStream.id);

      // Store tracks
      const videoTrack = mediaStream.getVideoTracks()[0];
      const audioTrack = mediaStream.getAudioTracks()[0];
      
      console.log('Media stream obtained:', {
        hasVideo: !!videoTrack,
        hasAudio: !!audioTrack,
        videoEnabled: videoTrack?.enabled,
        audioEnabled: audioTrack?.enabled,
      });
      
      videoTrackRef.current = videoTrack || null;
      audioTrackRef.current = audioTrack;

      // Apply initial states for video
      if (videoTrack) {
        // Always enable video track if it was requested
        if (constraints.video) {
          videoTrack.enabled = true;
          setWebcamEnabled(true);
          console.log('Video track enabled:', videoTrack.id, videoTrack.label);
        } else {
          videoTrack.enabled = false;
          setWebcamEnabled(false);
        }
      } else if (constraints.video) {
        // Video was requested but not available
        setWebcamEnabled(false);
        console.warn('Video was requested but no video track available');
      }
      
      if (audioTrack) {
        // Always enable audio track if audio was requested (user can mute later)
        if (constraints.audio) {
          audioTrack.enabled = true;
          setMicrophoneEnabled(true);
        } else {
          audioTrack.enabled = false;
          setMicrophoneEnabled(false);
        }
      } else if (constraints.audio) {
        // Audio was requested but not available
        setMicrophoneEnabled(false);
        console.warn('Audio was requested but no audio track available');
      } else {
        setMicrophoneEnabled(false);
      }

      setStream(mediaStream);

      // Create MediaRecorder for audio only (only if audio track exists)
      if (!audioTrack) {
        throw new Error('Audio track is required but not available');
      }

      const audioStream = new MediaStream([audioTrack]);
      const mediaRecorder = new MediaRecorder(audioStream, {
        mimeType: 'audio/webm',
      });

      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
          // Only send data if microphone is enabled (not muted)
          // Check the ref which always has the current track state
          if (onDataAvailable && audioTrackRef.current && audioTrackRef.current.enabled) {
            onDataAvailable(event.data);
          }
        }
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);

      return mediaStream;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to access media devices';
      setError(message);
      setIsRecording(false);
      // Clean up any tracks we might have created
      if (videoTrackRef.current) {
        try {
          videoTrackRef.current.stop();
        } catch (e) {
          // Ignore errors during cleanup
        }
        videoTrackRef.current = null;
      }
      if (audioTrackRef.current) {
        try {
          audioTrackRef.current.stop();
        } catch (e) {
          // Ignore errors during cleanup
        }
        audioTrackRef.current = null;
      }
      throw new Error(message);
    }
  }, []);

  const toggleWebcam = useCallback(() => {
    if (videoTrackRef.current) {
      videoTrackRef.current.enabled = !videoTrackRef.current.enabled;
      setWebcamEnabled(videoTrackRef.current.enabled);
    }
  }, []);

  const toggleMicrophone = useCallback(() => {
    if (audioTrackRef.current) {
      const newState = !audioTrackRef.current.enabled;
      audioTrackRef.current.enabled = newState;
      setMicrophoneEnabled(newState);
      console.log('Microphone toggled:', newState ? 'ON' : 'OFF');
    } else {
      console.warn('Cannot toggle microphone: audio track not available');
    }
  }, []);

  const stopStream = useCallback(() => {
    // Stop media recorder
    if (mediaRecorderRef.current) {
      if (mediaRecorderRef.current.state !== 'inactive') {
        try {
          mediaRecorderRef.current.stop();
        } catch (e) {
          console.warn('Error stopping MediaRecorder:', e);
        }
      }
      mediaRecorderRef.current = null;
    }

    // Stop all tracks from current stream state
    if (stream) {
      stream.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch (e) {
          console.warn('Error stopping track:', e);
        }
      });
      setStream(null);
    }

    // Also stop tracks from refs as a fallback
    if (videoTrackRef.current) {
      try {
        videoTrackRef.current.stop();
      } catch (e) {
        console.warn('Error stopping video track:', e);
      }
      videoTrackRef.current = null;
    }

    if (audioTrackRef.current) {
      try {
        audioTrackRef.current.stop();
      } catch (e) {
        console.warn('Error stopping audio track:', e);
      }
      audioTrackRef.current = null;
    }

    // Clear chunks
    chunksRef.current = [];
    
    // Update state
    setIsRecording(false);
    setError(null);
  }, [stream]);

  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [stream]);

  // Update enabled states when tracks change
  useEffect(() => {
    if (videoTrackRef.current) {
      setWebcamEnabled(videoTrackRef.current.enabled);
    }
    if (audioTrackRef.current) {
      const enabled = audioTrackRef.current.enabled;
      setMicrophoneEnabled(enabled);
      console.log('Audio track state updated:', enabled);
    }
  }, [stream]);

  return {
    stream,
    isRecording,
    error,
    webcamEnabled,
    microphoneEnabled,
    startStream,
    stopStream,
    toggleWebcam,
    toggleMicrophone,
  };
}
