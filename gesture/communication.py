"""Translate a sequence of observations into deliberate communication events."""
from dataclasses import dataclass, field
import math

from .rules import GESTURES, NO_HAND, UNKNOWN


class Confirmation:
    """One communication channel. A second hand pauses input for both."""
    def __init__(self, hold_ms=500, release_ms=350, max_gap_ms=250):
        for value in (hold_ms, release_ms, max_gap_ms):
            if not math.isfinite(value) or value <= 0:
                raise ValueError("Hold, release and maximum frame gap must be positive")
        self.hold_ms = hold_ms
        self.release_ms = release_ms
        self.max_gap_ms = max_gap_ms
        self.last_time = None
        self.candidate = None
        self.since = None
        self.latched = None
        self.status = "Ready"

    def update(self, labels, now_ms):
        """Pass one label per detected hand. Empty list means confirmed absence."""
        if not math.isfinite(now_ms) or (self.last_time is not None and now_ms < self.last_time):
            raise ValueError("Observation time must be finite and non-decreasing")
        if self.last_time is not None and now_ms - self.last_time > self.max_gap_ms:
            self.candidate = None  # Unobserved time is never evidence of a hold or release.
        self.last_time = now_ms
        label = NO_HAND
        if labels:
            label = labels[0] if len(labels) == 1 else UNKNOWN
        if label != self.candidate:
            self.candidate = label
            self.since = now_ms
        elapsed = now_ms - self.since
        if not labels and elapsed >= self.release_ms:
            self.latched = None

        if len(labels) > 1:
            self.status = "Two hands visible - use one hand"
        elif self.latched is not None:
            self.status = f"Confirmed {self.latched} - lower hand to repeat"
        elif not labels:
            self.status = "Ready"
        elif label not in GESTURES:
            self.status = "Pose unclear"
        elif elapsed < self.hold_ms:
            self.status = f"Hold {label} ({int(elapsed)}/{self.hold_ms:g} ms)"
        else:
            self.latched = label
            self.status = f"Confirmed {label} - lower hand to repeat"
            return label
        return None


DEFAULT_PHRASES = {
    "Open Palm": "Hello.",
    "Fist": "Please wait.",
    "Point": "Look there.",
    "V Sign": "Yes.",
    "Pinch": "Thank you.",
}


@dataclass
class Transcript:
    phrases: dict = field(default_factory=lambda: DEFAULT_PHRASES.copy())
    messages: list[str] = field(default_factory=list)

    def confirm(self, label):
        phrase = self.phrases[label]
        self.messages.append(phrase)
        return phrase

    def undo(self):
        if self.messages:
            self.messages.pop()

    def clear(self):
        self.messages.clear()
