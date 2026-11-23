"""OpenCV preview, editable phrase mapping and optional OS speech."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import cv2
import numpy as np

from .communication import DEFAULT_PHRASES

WINDOW = "Hand Landmark Tracker"


def load_phrases(path):
    phrases = DEFAULT_PHRASES.copy()
    if path:
        custom = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(custom, dict):
            raise ValueError("Phrase file must contain a JSON object")
        for name, phrase in custom.items():
            if name not in phrases or not isinstance(phrase, str):
                raise ValueError(f"Invalid gesture or phrase for {name!r}")
            if not phrase.strip() or len(phrase) > 160 or not phrase.isprintable():
                raise ValueError("Phrases must contain 1 to 160 printable characters")
            phrases[name] = phrase.strip()
    return phrases


class Speech:
    def __init__(self, enabled):
        self.command = None
        self.process = None
        if enabled:
            for name, args in [("espeak-ng", ["--stdin"]), ("espeak", ["--stdin"]),
                               ("say", ["-f", "-"])]:
                binary = shutil.which(name)
                if binary:
                    self.command = [binary, *args]
                    break
            if not self.command:
                print("Speech unavailable. Install eSpeak NG or use macOS say. Text is active.",
                      file=sys.stderr)

    def check(self):
        if self.process is None:
            return
        code = self.process.poll()
        if code is not None:
            self.process = None
            if code:
                self.command = None
                print(f"Speech exited with status {code}. Text is active.", file=sys.stderr)

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=.5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.process = None

    def speak(self, phrase):
        if self.command:
            self.stop()
            try:
                self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE)
                with self.process.stdin as stream:
                    stream.write((phrase + "\n").encode("utf-8"))
            except OSError as error:
                self.stop()
                print(f"Speech unavailable: {error}. Text is active.", file=sys.stderr)
                self.command = None


def draw(frame, hands, connections, status, messages, trial_text):
    def line(image, text, at, color=(240, 240, 240)):
        cv2.putText(image, text, at, cv2.FONT_HERSHEY_SIMPLEX, .62, color, 2, cv2.LINE_AA)

    if not hands:
        line(frame, "Gesture: No hand", (10, 28), (0, 255, 255))
    for i, hand in enumerate(hands):
        if len(hand.pixels) == 21 and np.isfinite(hand.pixels).all():
            points = [(int(x), int(y)) for x, y in hand.pixels]
            for edge in connections:
                cv2.line(frame, points[edge.start], points[edge.end], (255, 100, 40), 2)
            for point in points:
                cv2.circle(frame, point, 4, (0, 255, 0), -1)
        line(frame, f"Gesture: {hand.label}", (10, 28 + i * 28), (0, 255, 0))

    # Permanent dark text panel keeps feedback legible on a busy background.
    panel_width = max(780, frame.shape[1])
    preview = cv2.copyMakeBorder(frame, 0, 155, 0, panel_width - frame.shape[1],
                                 cv2.BORDER_CONSTANT, value=(24, 24, 24))
    y = frame.shape[0]
    line(preview, status, (10, y + 27), (150, 255, 200))
    latest = messages[-1] if messages else "(empty)"
    caption = f"Message {len(messages)}: {latest}"
    while cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX, .62, 2)[0][0] > panel_width - 50:
        caption = caption[:-1]
    if caption != f"Message {len(messages)}: {latest}":
        caption += "..."
    line(preview, caption, (10, y + 58))
    line(preview, trial_text or "Lower your hand between messages.", (10, y + 92))
    line(preview, "M measures   - trial   U undo   C clear   Q quit", (10, y + 130))
    cv2.imshow(WINDOW, preview)
