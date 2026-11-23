"""Exercise the public application entry point with a temporary MJPEG video."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from gesture.session import Observation
import hand_detector


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.video = str(Path(tmp.name) / "rest.avi")
        writer = cv2.VideoWriter(self.video, cv2.VideoWriter_fourcc(*"MJPG"), 10, (160, 120))
        self.assertTrue(writer.isOpened(), "Test needs OpenCV MJPEG video support")
        try:
            for _ in range(8):
                writer.write(np.zeros((120, 160, 3), dtype=np.uint8))
        finally:
            writer.release()

    def test_real_no_hand_inference_and_replay_clock(self):
        stdout = StringIO()
        with redirect_stdout(stdout):
            status = hand_detector.main(["--headless", "--video", self.video, "--trace"])
        self.assertEqual(status, 0)
        rows = [json.loads(line) for line in stdout.getvalue().splitlines()]
        self.assertEqual([r["time_ms"] for r in rows], list(range(0, 800, 100)))
        self.assertTrue(all(r["labels"] == [] and r["event"] is None for r in rows))

    def test_preview_controls_and_one_message(self):
        palm = Observation("Open Palm", [], {})
        keys = [ord("m"), -1, ord("u"), ord("-"), ord("c"), ord("q")]
        stdout, stderr = StringIO(), StringIO()
        with (patch.dict(os.environ, DISPLAY=":test"),
              patch("hand_detector.observe", return_value=[palm]) as observe,
              patch.object(cv2, "imshow") as display,
              patch.object(cv2, "waitKey", side_effect=keys),
              patch.object(cv2, "destroyAllWindows") as close,
              redirect_stdout(stdout), redirect_stderr(stderr)):
            status = hand_detector.main(["--video", self.video, "--hold-ms", "100"])
        self.assertEqual(status, 0)
        self.assertEqual(display.call_count, len(keys))
        close.assert_called_once()
        self.assertTrue(observe.call_args_list[1].args[-1])
        self.assertEqual(stdout.getvalue().splitlines(), ["Open Palm: Hello."])
        self.assertEqual(stderr.getvalue().count("Text: (empty)"), 2)

    def test_bad_source_model_and_threshold(self):
        for args in [["--video", self.video + ".missing"], ["--model", self.video + ".missing"],
                     ["--pinch-gap", "nan"], ["--release-ms", "0"]]:
            with self.subTest(args=args), redirect_stderr(StringIO()) as err:
                self.assertEqual(hand_detector.main(["--headless", *args]), 1)
                self.assertIn("Hand tracker:", err.getvalue())
