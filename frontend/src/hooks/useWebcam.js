import { useState, useRef, useEffect, useCallback } from 'react';

export function useWebcam() {
  const [stream, setStream] = useState(null);
  const [isEnabled, setIsEnabled] = useState(false);
  const [permission, setPermission] = useState('unknown'); // 'unknown' | 'granted' | 'denied'
  const [error, setError] = useState(null);
  const videoRef = useRef(null);

  const stopTracks = useCallback((mediaStream) => {
    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch {
          // ignore
        }
      });
    }
  }, []);

  const enable = useCallback(async () => {
    setError(null);
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setError('Webcam is not supported in this browser.');
      setPermission('denied');
      return false;
    }

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 320, height: 240, facingMode: 'user' },
        audio: false,
      });

      setStream(mediaStream);
      setIsEnabled(true);
      setPermission('granted');

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play().catch(() => {});
      }
      return true;
    } catch (err) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setPermission('denied');
        setError('Camera access was denied in browser permissions.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setError('No camera device found on this system.');
      } else {
        setError(`Camera error: ${err.message || 'Unknown error'}`);
      }
      setIsEnabled(false);
      return false;
    }
  }, []);

  const disable = useCallback(() => {
    stopTracks(stream);
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setStream(null);
    setIsEnabled(false);
  }, [stream, stopTracks]);

  // Sync video element when stream or videoRef changes
  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
      videoRef.current.play().catch(() => {});
    }
  }, [stream]);

  // Clean up all tracks on unmount
  useEffect(() => {
    return () => {
      stopTracks(stream);
    };
  }, [stream, stopTracks]);

  // Capture frame as base64 JPEG
  const captureFrame = useCallback(() => {
    if (!videoRef.current || !stream || !isEnabled) return null;
    try {
      const video = videoRef.current;
      if (video.videoWidth === 0 || video.videoHeight === 0) return null;
      const canvas = document.createElement('canvas');
      canvas.width = 224;
      canvas.height = 224;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, 224, 224);
      return canvas.toDataURL('image/jpeg', 0.8);
    } catch {
      return null;
    }
  }, [stream, isEnabled]);

  return {
    videoRef,
    stream,
    isEnabled,
    permission,
    error,
    enable,
    disable,
    captureFrame,
  };
}
