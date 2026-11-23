"""Run the webcam communicator or replay a constant-frame-rate recording."""
import argparse
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import sys
import time

from gesture.communication import Confirmation, Transcript
from gesture.geometry import calculate_angle  # Preserve the original importable helper.
from gesture.rules import Thresholds
from gesture.session import PracticeTrial, observe


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    source = cli.add_mutually_exclusive_group()
    source.add_argument("--camera", type=int, default=0, help="camera device index (default 0)")
    source.add_argument("--video", help="path to a constant-frame-rate video")
    cli.add_argument("--headless", action="store_true", help="omit the preview and keyboard controls")
    cli.add_argument("--trace", action="store_true", help="emit one JSON object per frame to stdout")
    cli.add_argument("--geometry", choices=["2d", "image3d", "world3d"], default="2d")
    cli.add_argument("--model", type=Path, default=Path(__file__).with_name("hand_landmarker.task"))
    cli.add_argument("--hold-ms", type=int, default=500)
    cli.add_argument("--release-ms", type=int, default=350)
    cli.add_argument("--max-gap-ms", type=int, default=250)
    for name, value in asdict(Thresholds()).items():
        cli.add_argument("--" + name.replace("_", "-"), type=float, default=value)
    cli.add_argument("--phrases", help="JSON file overriding gesture-to-phrase mappings")
    cli.add_argument("--speak", action="store_true", help="enable optional local speech")
    return cli


def run(args):
    import cv2
    import mediapipe as mp

    from gesture.interface import Speech, draw, load_phrases

    limits = Thresholds(**{key: getattr(args, key) for key in asdict(Thresholds())})
    confirmation = Confirmation(args.hold_ms, args.release_ms, args.max_gap_ms)
    transcript = Transcript(load_phrases(args.phrases))
    if not args.model.is_file():
        raise ValueError(f"Missing MediaPipe task bundle: {args.model}")
    speech = Speech(args.speak)
    vision = mp.tasks.vision
    options = vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(args.model)),
        running_mode=vision.RunningMode.VIDEO, num_hands=2,
    )
    connections = vision.HandLandmarksConnections.HAND_CONNECTIONS
    source = args.video if args.video is not None else args.camera
    camera = cv2.VideoCapture(source)
    index = 0
    previous_ms = -1
    trial = None
    trial_text = ""
    diagnostics = False
    window_created = False
    try:
        if not camera.isOpened():
            raise RuntimeError(f"Cannot open {source!r}. Check the video path or camera permissions/index.")
        if (not args.headless and sys.platform.startswith("linux")
                and not (os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"))):
            raise RuntimeError("No display session. Use --headless or run from a desktop.")
        fps = camera.get(cv2.CAP_PROP_FPS) if args.video else None
        if args.video and (not math.isfinite(fps) or not 0 < fps <= 1000):
            raise ValueError("Replay requires a video with a valid frame rate of at most 1000 FPS")
        with vision.HandLandmarker.create_from_options(options) as detector:
            while True:
                success, frame = camera.read()
                if not success:
                    if args.video and index:
                        break
                    raise RuntimeError(f"Could not read frame {index} from {source!r}.")
                # Replay uses media time even if the decoder runs faster than real time.
                now = round(index * 1000 / fps) if args.video else time.monotonic_ns() // 1_000_000
                timestamp = max(now, previous_ms + 1)
                previous_ms = timestamp
                image = mp.Image(image_format=mp.ImageFormat.SRGB,
                                 data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                result = detector.detect_for_video(image, timestamp)
                height, width = frame.shape[:2]
                hands = observe(result, width, height, args.geometry, limits, diagnostics)
                labels = [hand.label for hand in hands]
                event = confirmation.update(labels, now)
                phrase = transcript.confirm(event) if event else None
                speech.check()
                if phrase:
                    speech.speak(phrase)
                    if not args.trace:
                        print(f"{event}: {phrase}", flush=True)
                if args.trace:
                    print(json.dumps(dict(frame=index, time_ms=now, labels=labels, event=event,
                                          phrase=phrase), ensure_ascii=False), flush=True)
                if diagnostics:
                    print([hand.features for hand in hands] or "No hand to measure", file=sys.stderr)
                    diagnostics = False
                if trial:
                    trial_text = trial.update(now, labels, event)
                    if trial.done:
                        trial = None
                index += 1
                if args.headless:
                    continue
                draw(frame, hands, connections, confirmation.status, transcript.messages, trial_text)
                window_created = True
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:
                    break
                if key == ord("m"):
                    diagnostics = True
                elif key == ord("-"):
                    trial = PracticeTrial(now, args.hold_ms)
                elif key in (ord("c"), ord("u")):
                    if key == ord("c"):
                        transcript.clear()
                    else:
                        transcript.undo()
                    speech.stop()
                    print("Text:", " ".join(transcript.messages) or "(empty)", file=sys.stderr)
    except cv2.error as error:
        raise RuntimeError(f"OpenCV capture or display failed: {error}") from error
    finally:
        camera.release()
        speech.stop()
        if window_created:
            cv2.destroyAllWindows()


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        run(args)
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError, RuntimeError, ImportError) as error:
        print(f"Hand tracker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
