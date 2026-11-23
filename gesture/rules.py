"""Conservative one-hand static pose vocabulary."""
from dataclasses import dataclass
import math

from .geometry import Features

UNKNOWN = "Unknown"
NO_HAND = "No hand"
GESTURES = ("Open Palm", "Fist", "Point", "V Sign", "Pinch")


@dataclass(frozen=True)
class Thresholds:
    straight: float = 155
    curled: float = 115
    pinch_gap: float = 0.22
    v_spread: float = 0.40
    fist_thumb_reach: float = 1.05

    def __post_init__(self):
        if not 0 < self.curled < self.straight <= 180:
            raise ValueError("Require 0 < curled < straight <= 180 degrees")
        for value in (self.pinch_gap, self.v_spread, self.fist_thumb_reach):
            if not math.isfinite(value) or value <= 0:
                raise ValueError("Distance thresholds must be positive and finite")


def classify(features: Features | None, limits: Thresholds = Thresholds()) -> str:
    if features is None:
        return UNKNOWN
    straight = tuple(min(p, d) >= limits.straight
                     for p, d in zip(features.pip, features.dip))
    curled = tuple(p <= limits.curled for p in features.pip)
    index, middle, ring, little = straight
    # Our pinch convention keeps at least two other fingers extended.
    if features.thumb_index_gap <= limits.pinch_gap and sum(straight[1:]) >= 2:
        return "Pinch"
    if all(straight):
        return "Open Palm"
    if all(curled) and features.thumb_palm_gap <= limits.fist_thumb_reach:
        return "Fist"
    if index and all(curled[1:]):
        return "Point"
    if index and middle and all(curled[2:]) and features.spread >= limits.v_spread:
        return "V Sign"
    return UNKNOWN
