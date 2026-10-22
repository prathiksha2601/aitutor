"""
app/computer_vision/aggregator.py
Temporal aggregation service for noisy facial-expression predictions.
Smooths over time windows and prevents spamming suggestions.
"""

from collections import deque, Counter
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

SUGGESTION_OPTIONS = [
    "Explain more simply.",
    "Give a practical example.",
    "Ask me a practice question.",
    "Continue learning.",
]


class TemporalAggregator:
    """
    Collects a limited window of valid expression predictions.
    Requires sufficient valid observations before generating a learning-support suggestion.
    """

    def __init__(
        self,
        window_size: int = 10,
        min_valid: int = 5,
        stale_seconds: int = 30,
        cooldown_seconds: int = 60,
    ):
        self.window_size = window_size
        self.min_valid = min_valid
        self.stale_seconds = stale_seconds
        self.cooldown_seconds = cooldown_seconds

        self.observations: deque = deque(maxlen=window_size)
        self.last_suggestion_time: datetime | None = None
        self.is_dismissed: bool = False

    def add_observation(self, category: str, confidence: float) -> None:
        """Add an expression observation with timestamp."""
        now = datetime.now(timezone.utc)
        self.observations.append({
            "category": category,
            "confidence": confidence,
            "timestamp": now,
        })
        self._prune_stale(now)

    def _prune_stale(self, now: datetime) -> None:
        """Remove observations older than stale_seconds."""
        cutoff = now - timedelta(seconds=self.stale_seconds)
        while self.observations and self.observations[0]["timestamp"] < cutoff:
            self.observations.popleft()

    def get_aggregated(self) -> dict | None:
        """
        Return aggregated summary if sufficient valid observations exist.
        Returns None otherwise.
        """
        now = datetime.now(timezone.utc)
        self._prune_stale(now)

        if len(self.observations) < self.min_valid:
            return None

        counts = Counter(obs["category"] for obs in self.observations)
        dominant_category, count = counts.most_common(1)[0]
        avg_confidence = sum(obs["confidence"] for obs in self.observations) / len(self.observations)

        return {
            "dominant_category": dominant_category,
            "dominant_count": count,
            "total_observations": len(self.observations),
            "average_confidence": round(avg_confidence, 3),
            "category_counts": dict(counts),
        }

    def should_suggest(self) -> bool:
        """
        Determine whether a learning-support suggestion should be offered.
        Requires sufficient observations, non-dismissed state, and cooldown elapsed.
        """
        if self.is_dismissed:
            return False

        agg = self.get_aggregated()
        if not agg:
            return False

        now = datetime.now(timezone.utc)
        if self.last_suggestion_time:
            elapsed = (now - self.last_suggestion_time).total_seconds()
            if elapsed < self.cooldown_seconds:
                return False

        # Check if dominant category might indicate learning struggle
        # Note: Expressions are ambiguous; we only offer help gently
        struggle_categories = {"sad", "fear", "angry"}
        if agg["dominant_category"] in struggle_categories:
            return True

        return False

    def trigger_suggestion(self) -> dict | None:
        """Record suggestion trigger and return suggestion payload."""
        if not self.should_suggest():
            return None

        now = datetime.now(timezone.utc)
        self.last_suggestion_time = now

        return {
            "text": "Would you like some extra help with this concept?",
            "options": SUGGESTION_OPTIONS,
            "timestamp": now.isoformat(),
        }

    def dismiss(self) -> None:
        """Student dismissed the suggestion."""
        self.is_dismissed = True

    def reset_dismissal(self) -> None:
        """Re-allow suggestions after explicit user interaction."""
        self.is_dismissed = False

    def clear(self) -> None:
        """Reset observations window."""
        self.observations.clear()
        self.is_dismissed = False
