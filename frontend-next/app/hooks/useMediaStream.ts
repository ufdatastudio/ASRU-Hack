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
        // Ensure audio track starts enabled if audio is requested
        audioTrack.enabled = microphoneEnabled && constraints.audio;
        setMicrophoneEnabled(audioTrack.enabled);
      } else if (!constraints.audio) {
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
      throw new Error(message);
    }
  }, [webcamEnabled, microphoneEnabled]);

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
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }

    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }

    videoTrackRef.current = null;
    audioTrackRef.current = null;
    setIsRecording(false);
    mediaRecorderRef.current = null;
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
