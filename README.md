# Hand-Gesture-Recognition

Computer Vision-Based Hand Gesture Recognition System for Accessible Communication.

This desktop prototype maps five deliberate, static, one-handed poses to editable text and optional speech. Look at the preview to see the detected pose. Hold until the confirmation appears, then move your hand out of view before the next message. The phrases below are examples you can change. This vocabulary is a set of communication shortcuts.

## Install and start

Use the `ai-development` branch and run these commands from the repository root. The tested combination is CPython 3.12 on x86-64 Linux. The desktop preview needs a working OpenCV GUI backend, a display session and camera permission. The CPU runs inference with the included `hand_landmarker.task`.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python hand_detector.py
```

On Windows use `py -3.12 -m venv .venv` followed by `.venv\Scripts\Activate.ps1` in PowerShell. Availability of wheels and camera backends depends on the platform. On minimal Linux systems the native libraries for OpenCV and MediaPipe must also be installed. For a missing `libGLESv2.so.2` on Debian/Ubuntu, the system package is `libgles2`. Use the GUI-capable OpenCV distribution in the manifest; installing multiple OpenCV wheels into one environment can break the shared `cv2` import.

```sh
python hand_detector.py --camera 1
python hand_detector.py --hold-ms 700 --release-ms 450
python hand_detector.py --help
```

### Use the communicator

| Pose | How the default rules interpret it | Default phrase |
|---|---|---|
| Open Palm | Extend all four long fingers, keeping thumb and index tips apart. | Hello. |
| Fist | Curl all four long fingers and bring the thumb close to the palm. | Please wait. |
| Point | Extend the index finger and curl the other three. | Look there. |
| V Sign | Extend and separate index and middle fingers; curl ring and little fingers. | Yes. |
| Pinch | Bring thumb and index tips together with at least two of middle, ring and little fingers extended. | Thank you. |
| Unknown | A hand is present but its geometry is ambiguous, unsupported or invalid. | No message |
| No hand | The detector sees no hands. Sustained absence re-arms the communicator. | No message |

Use one hand at a time. The preview labels up to two hands. When both appear, pending confirmation stops and the status explains how to resume. Default hold is 500 ms. Once confirmed, a pose stays latched until at least 350 ms of observed absence. Changing directly to another pose does not emit another message. A gap above 250 ms between observations interrupts pending hold or release evidence. At consistently low frame rates, inspect frame timestamps before increasing `--max-gap-ms`. A larger tolerance also admits more unseen movement.

With the preview window focused, use lowercase keys.

| Key | Action |
|---|---|
| `m` | Print the next frame's per-hand measurements for all three geometry modes to the terminal. |
| `-` | Start a three-second practice countdown. Keep both hands down until the cue, then hold Open Palm. The result includes reaction and hold time. |
| `u` | Undo the last phrase. |
| `c` | Clear the transcript. |
| `q` or Esc | Quit. In headless mode use Ctrl+C. |

The panel shows the latest phrase and message count. The terminal prints each confirmed phrase and the corrected transcript after edits. The transcript exists in memory for this session. Editing removes text from the transcript; already spoken words remain audible to the listener. OpenCV's preview font has limited character coverage. The terminal and speech backend receive the original phrase text.

### Customize phrases and speech

Create a UTF-8 JSON file containing just the mappings to override, for example:

```json
{"Point": "Water, please.", "Open Palm": "I would like to speak."}
```

```sh
python hand_detector.py --phrases phrases.json --speak
```

Speech is off by default. With `--speak`, the app looks for `espeak-ng`, `espeak` or macOS `say` on PATH. A missing or failed speech engine leaves text active. Each new phrase can interrupt unfinished speech. Undo, clear and quit stop active speech.

## Replay and test

Use a constant-frame-rate video supported by OpenCV. Replay runs at decoder speed but uses the video's media time to confirm holds. The same detector, rules and confirmation code handle camera and video frames.

```sh
python hand_detector.py --video trial.mp4
python hand_detector.py --video trial.mp4 --headless --trace > trial.jsonl
python hand_detector.py --video trial.mp4 --headless --trace --geometry world3d > world.jsonl
python -m unittest discover -s tests -v
```

Each JSON line contains the frame index, timestamp in milliseconds, detected labels, confirmed event and phrase. An empty labels array represents No hand. An event is null on frames without a new confirmation. MediaPipe diagnostics go to standard error. The test suite uses temporary short videos and the bundled model. Automated verification requires neither a webcam nor an audio device.

## Architecture

| Module | Responsibility |
|---|---|
| `hand_detector.py` | CLI, OpenCV capture or file replay, monotonic timestamps, MediaPipe VIDEO inference and resource cleanup. |
| `gesture/geometry.py` | Interior angles, palm normalization, per-finger flexion, thumb posture, fingertip distances and validity checks. |
| `gesture/rules.py` | Configurable thresholds, five pose definitions and rejection. |
| `gesture/session.py` | Convert each MediaPipe result into observations and manage the optional prompted trial. |
| `gesture/communication.py` | Consume one timestamped list of labels per frame, confirm holds, detect release and edit the transcript. |
| `gesture/interface.py` | Draw the preview and status panel, load phrase mappings and manage local speech. |
| `tests/` | Geometry, classification, confirmation, input errors and application-entry integration checks. |

The original model, dot-product angle method, landmark skeleton, optional measurements and Python learning exercises are retained. The classifier now requires specific finger configurations. An unusable or unfamiliar pose returns Unknown. The former three-or-four-straight-fingers rule and hand-presence stopwatch have been replaced. PIP refers to the middle joint of each long finger, DIP to its distal joint, and MCP to the knuckle at its base.

**Geometry modes.** The default `2d` uses unrounded pixel coordinates. `image3d` adds the image landmark's estimated z scaled by image width. `world3d` uses the separate estimated world-landmark output, and rejects a missing world hand. All lengths used in classification are divided by palm width. The straight and curled thresholds are in degrees. The pinch gap, V spread and fist thumb reach are fractions of palm width. Use `--straight`, `--curled`, `--pinch-gap`, `--v-spread` and `--fist-thumb-reach` to experiment.

**Known limits.** Static rules can confuse out-of-plane bends and projected contact. Very narrow or partially occluded palms can be rejected. Tracking loss lasting the release duration can re-arm a held gesture. Two hands pause output and there is no persistent identity between people. Constant-rate timestamps are unsuitable for variable-frame-rate timing studies. A decoder failure partway through a recording may appear as end of file; check the processed frame count. Comfortable gestures, usable dwell times, speaker audibility and live latency need validation with intended users.

See the [evaluation record and experiment protocol](EVALUATION.md) and the [engineering learning log](LEARNING_LOG.md).
