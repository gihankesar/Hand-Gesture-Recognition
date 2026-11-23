from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from gesture.interface import load_phrases
from gesture.rules import Thresholds
from gesture.session import PracticeTrial, observe


class SessionTests(unittest.TestCase):
    def test_trial_requires_rest_target_and_deadline(self):
        trial = PracticeTrial(100, 500)
        trial.update(3200, ["Open Palm"], "Open Palm")
        self.assertFalse(trial.done)
        trial.update(3300, [], None)
        trial.update(3400, ["Point"], "Point")
        self.assertFalse(trial.done)
        self.assertIn("confirmed", trial.update(5000, ["Open Palm"], "Open Palm"))
        expired = PracticeTrial(0, 500)
        expired.update(3000, [], None)
        self.assertIn("timed out", expired.update(5000, ["Open Palm"], "Open Palm"))

    def test_observe_absent_and_missing_world(self):
        result = SimpleNamespace(hand_landmarks=[], hand_world_landmarks=[])
        self.assertEqual(observe(result, 640, 480, "2d", Thresholds()), [])
        result.hand_landmarks = [[SimpleNamespace(x=.5, y=.5, z=0)]*21]
        hands = observe(result, 640, 480, "world3d", Thresholds(), diagnostics=True)
        self.assertEqual(hands[0].label, "Unknown")
        self.assertEqual(set(hands[0].features), {"2d", "image3d", "world3d"})

    def test_custom_phrases(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "phrases.json"
            path.write_text('{"Point": "Water, please."}')
            self.assertEqual(load_phrases(path)["Point"], "Water, please.")
            for data in ["null", '{"Point": ""}', '{"Other": "No"}']:
                path.write_text(data)
                with self.assertRaises(ValueError):
                    load_phrases(path)
