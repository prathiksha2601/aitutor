import { useState, useRef, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner.jsx';

export default function VideoPlayer({
  videoUrl,
  videoType = 'youtube',
  title = '',
  initialPosition = 0,
  onTimeUpdate = null,
  onEnded = null,
}) {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Resume playback position on HTML5 video
  useEffect(() => {
    if (videoRef.current && initialPosition > 0 && videoType !== 'youtube') {
      try {
        videoRef.current.currentTime = initialPosition;
      } catch {
        // May fail if metadata not yet loaded
      }
    }
  }, [initialPosition, videoType]);

  const handleTimeUpdate = () => {
    if (videoRef.current && onTimeUpdate) {
      onTimeUpdate(videoRef.current.currentTime);
    }
  };

  if (!videoUrl) {
    return (
      <div className="video-wrapper">
        <div className="video-overlay-state">
          <p style={{ fontSize: '1.1rem', fontWeight: '600' }}>No video configured for this lesson</p>
          <p style={{ fontSize: '0.85rem', opacity: 0.8 }}>Use the AI Tutor to explore this topic interactively.</p>
        </div>
      </div>
    );
  }

  // Handle YouTube embed URLs
  if (videoType === 'youtube' || videoUrl.includes('youtube.com') || videoUrl.includes('youtu.be')) {
    // Ensure embed format
    let embedUrl = videoUrl;
    if (embedUrl.includes('watch?v=')) {
      embedUrl = embedUrl.replace('watch?v=', 'embed/');
    }
    const startParam = initialPosition > 0 ? `?start=${Math.floor(initialPosition)}` : '';

    return (
      <div className="video-wrapper">
        <iframe
          src={`${embedUrl}${startParam}`}
          title={title || 'Educational Video'}
          className="video-iframe"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    );
  }

  // HTML5 Video
  return (
    <div className="video-wrapper">
      {isLoading && (
        <div className="video-overlay-state">
          <LoadingSpinner message="Loading video..." />
        </div>
      )}
      {hasError ? (
        <div className="video-overlay-state">
          <p style={{ fontWeight: '700' }}>Unable to load video</p>
          <p style={{ fontSize: '0.85rem' }}>Check network connection or try reloading.</p>
        </div>
      ) : (
        <video
          ref={videoRef}
          src={videoUrl}
          className="video-player"
          controls
          onTimeUpdate={handleTimeUpdate}
          onEnded={onEnded}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onError={() => setHasError(true)}
          onLoadStart={() => setIsLoading(true)}
          onLoadedData={() => setIsLoading(false)}
        >
          Your browser does not support the video tag.
        </video>
      )}
    </div>
  );
}
