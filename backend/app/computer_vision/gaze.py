"""
app/computer_vision/gaze.py
Optional approximate gaze direction estimation.
Treated strictly as an uncertain, secondary signal.
Gracefully degrades to 'unavailable' when MediaPipe is not installed.
"""

from datetime import datetime, timezone
import logging
import numpy as np

logger = logging.getLogger(__name__)


class GazeEstimator:
    """Estimates approximate horizontal/vertical gaze direction."""

    def __init__(self):
        self.available = False
        self._init_mediapipe()

    def _init_mediapipe(self) -> None:
        try:
            import mediapipe as mp
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self.available = True
            logger.info("MediaPipe FaceMesh gaze estimator initialised.")
        except Exception as exc:
            logger.info("MediaPipe not available for gaze estimation: %s", exc)
            self.available = False

    def is_available(self) -> bool:
        return self.available

    def estimate_gaze(self, image_bytes: bytes) -> dict:
        """
        Estimate approximate gaze direction.
        Returns 'center', 'left', 'right', 'up', 'down', or 'unavailable'.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        if not self.is_available():
            return {
                "status": "unavailable",
                "message": "MediaPipe gaze estimation is not available.",
                "direction": "unavailable",
                "timestamp": timestamp,
            }

        try:
            import cv2
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return {
                    "status": "error",
                    "direction": "unavailable",
                    "timestamp": timestamp,
                }

            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if not results.multi_face_landmarks:
                return {
                    "status": "ok",
                    "direction": "center",
                    "face_detected": False,
                    "confidence": 0.5,
                    "timestamp": timestamp,
                }

            landmarks = results.multi_face_landmarks[0].landmark
            # Approximate gaze direction from iris relative to eye corners (landmarks 468, 473 for irises)
            # If refinement landmarks available:
            if len(landmarks) > 468:
                left_iris = landmarks[468]
                left_outer = landmarks[33]
                left_inner = landmarks[133]
                eye_width = abs(left_inner.x - left_outer.x)
                if eye_width > 0.001:
                    ratio = (left_iris.x - left_outer.x) / eye_width
                    if ratio < 0.38:
                        direction = "right"
                    elif ratio > 0.62:
                        direction = "left"
                    else:
                        direction = "center"
                else:
                    direction = "center"
            else:
                direction = "center"

            return {
                "status": "ok",
                "direction": direction,
                "face_detected": True,
                "confidence": 0.7,
                "timestamp": timestamp,
                "uncertain_signal": True,
            }

        except Exception as exc:
            logger.warning("Gaze estimation error: %s", exc)
            return {
                "status": "error",
                "direction": "unavailable",
                "message": str(exc),
                "timestamp": timestamp,
            }
