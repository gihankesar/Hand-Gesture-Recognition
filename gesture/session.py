"""One-frame recognition, diagnostic measurements and a prompted practice trial."""
from dataclasses import dataclass

from .geometry import extract, image_points
from .rules import classify


@dataclass
class Observation:
    label: str
    pixels: list
    features: dict


def observe(result, width, height, geometry, limits, diagnostics=False):
    observations = []
    for i, hand in enumerate(result.hand_landmarks):
        pixels = image_points(hand, width, height)
        modes = ("2d", "image3d", "world3d") if diagnostics else (geometry,)
        features = {}
        for mode in modes:
            if mode == "2d":
                points = pixels
            elif mode == "image3d":
                points = image_points(hand, width, height, depth=True)
            else:
                world = result.hand_world_landmarks
                points = [(p.x, p.y, p.z) for p in world[i]] if i < len(world) else []
            features[mode] = extract(points)
        observations.append(Observation(classify(features[geometry], limits), pixels, features))
    return observations


class PracticeTrial:
    """Cue, then require observed rest followed by a newly confirmed open palm."""
    def __init__(self, start, hold_ms):
        self.cue = start + 3000
        self.deadline = self.cue + max(2000, hold_ms + 1500)
        self.rested = False
        self.done = False

    def update(self, now, labels, event):
        if now < self.cue:
            return f"Trial in {(self.cue - now)/1000:.1f}s - lower hands"
        if now >= self.deadline:
            self.done = True
            return "Trial timed out"
        if not labels:
            self.rested = True
        if not self.rested:
            return "Trial: lower both hands first"
        if event == "Open Palm":
            self.done = True
            return f"Open Palm confirmed {(now - self.cue)/1000:.2f}s after cue"
        return "Trial: show and hold Open Palm"
