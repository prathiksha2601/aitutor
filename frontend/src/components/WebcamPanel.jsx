import { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext.jsx';
import { api } from '../services/api.js';

export default function WebcamPanel({ webcam, onExpressionUpdate = null }) {
  const { webcamConsent, grantWebcamConsent, revokeWebcamConsent } = useApp();
  const [analyzing, setAnalyzing] = useState(false);
  const [lastPrediction, setLastPrediction] = useState(null);

  const { videoRef, isEnabled, permission, error, enable, disable, captureFrame } = webcam;

  const handleToggle = async () => {
    if (isEnabled) {
      disable();
      setLastPrediction(null);
    } else {
      await enable();
    }
  };

  // Periodic frame inference when enabled
  useEffect(() => {
    if (!isEnabled || !webcamConsent) return;

    const interval = setInterval(async () => {
      const frameB64 = captureFrame();
      if (!frameB64) return;

      try {
        setAnalyzing(true);
        const res = await api.analyzeExpression({
          image_b64: frameB64,
          consent: true,
        });

        if (res.data?.expression?.status === 'ok') {
          const exp = res.data.expression;
          setLastPrediction(exp);
          if (onExpressionUpdate) {
            onExpressionUpdate(exp);
          }
        }
      } catch {
        // Silently tolerate frame failures; predictions are optional
      } finally {
        setAnalyzing(false);
      }
    }, 10000); // Sample every 10 seconds

    return () => clearInterval(interval);
  }, [isEnabled, webcamConsent, captureFrame, onExpressionUpdate]);

  return (
    <div className="webcam-panel">
      <div className="webcam-header">
        <div className="webcam-title">
          <div className={`webcam-status-dot ${isEnabled ? 'active' : ''}`} />
          <span>Facial Expression Analysis</span>
        </div>
        <span className="badge badge-warning" style={{ fontSize: '0.7rem' }}>
          Optional
        </span>
      </div>

      {!webcamConsent ? (
        <div>
          <div className="consent-box">
            <strong>Privacy & Consent Notice:</strong>
            <p style={{ marginTop: '4px' }}>
              We respect your privacy. Webcam analysis is entirely optional and helps the tutor offer beginner-friendly explanations if you find a concept challenging.
              <strong> Raw video frames are never stored.</strong>
            </p>
          </div>
          <button onClick={grantWebcamConsent} className="btn btn-primary btn-sm" style={{ width: '100%' }}>
            Give Consent & Enable Analysis
          </button>
        </div>
      ) : (
        <div>
          <div className="webcam-preview-container">
            {isEnabled ? (
              <video ref={videoRef} autoPlay playsInline muted className="webcam-video" />
            ) : (
              <div className="webcam-placeholder">
                <p>Camera is disabled.</p>
                <p style={{ fontSize: '0.75rem', marginTop: '4px' }}>Click Enable to activate visual support signals.</p>
              </div>
            )}
          </div>

          {error && (
            <div className="alert alert-error" style={{ padding: '8px 12px', fontSize: '0.8rem', marginBottom: '8px' }}>
              {error}
            </div>
          )}

          {lastPrediction && (
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
              <span>Signal: <strong>{lastPrediction.category}</strong> (uncertain)</span>
              <span>Conf: {Math.round(lastPrediction.confidence * 100)}%</span>
            </div>
          )}

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={handleToggle}
              className={`btn btn-sm ${isEnabled ? 'btn-danger' : 'btn-primary'}`}
              style={{ flex: 1 }}
            >
              {isEnabled ? 'Stop Webcam' : 'Enable Webcam'}
            </button>
            <button
              onClick={revokeWebcamConsent}
              className="btn btn-outline btn-sm"
              title="Revoke Consent"
            >
              Revoke Consent
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
