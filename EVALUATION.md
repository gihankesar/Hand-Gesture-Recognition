# Evaluation record

## Evidence available at development time

| Check | Input | Observed result |
|---|---|---|
| Automated suite | Analytic joint geometry and full synthetic hands, boundary cases, timestamped label sequences, phrase mapping, error paths, and OpenCV/MediaPipe entry-point tests | 21 tests passed on Linux with CPython 3.12. A fresh environment installed from the manifest passed the suite and pip's dependency check. |
| Original application | A blank frame followed by the supplied two-palm photograph, through the original model | No hand, then two Open Palm overlays. Camera, keyboard and window were substituted. |
| Application replay | 53-frame MJPEG clip at 10 frames/s derived from that photograph | The 2D and image-relative 3D runs each emitted two greetings. Both hands together emitted none. The world-landmark run rejected the palm and emitted none. |
| Upstream reference landmarks | One world-landmark result each for fist, pointing up and victory | Fist classified as Fist. Point and V Sign returned Unknown under the default thresholds. |

### Replay detail

The photograph was 720 × 382, SHA-256 `240c082e80128ff1ca8a83ce645e2ba4d8bc30f0967b7991cf5fa375bab489e1`. It was available in the development environment. The photograph and derived recording are external fixtures. To reproduce the sequence from that image, encode six black frames, ten original frames, fourteen copies with the right half blacked out, nine black frames, then fourteen more single-palm frames. Use MJPEG at 10 frames/s. Run the CLI three times with `--video`, `--headless`, `--trace` and each geometry mode.

The two successful modes emitted at frames 21 and 44 (media times 2100 ms and 4400 ms). World mode returned Unknown for each visible palm. On the original picture, separate world estimates put the index PIP angles near 111° and 106°, below the 155° straight cutoff. All frames showing the hand came from one still. This verifies integration, including re-arming. It does not estimate accuracy, physical-camera FPS, or the time from a person's movement to a displayed message.

### Landmark-only check

The upstream MediaPipe fixtures provide 21 world points in x, y, z order. We passed the `world_landmarks` block directly to `extract` and then to `classify`. Image dimensions and camera inference are unnecessary for that check. The default Point case missed the 155° cutoff at its index DIP (148.4°). In the V example, middle PIP was 153.0° and index DIP was 144.1°. An exploratory rerun at `straight=140` classified all three fixtures as their named poses. That cutoff was tried after inspecting these examples. They cannot serve as an independent test of it. The shipping default is 155°.

[Upstream fist](https://github.com/google-ai-edge/mediapipe/blob/238640e0ac3948b3b137451e25976640e8a78c1d/mediapipe/tasks/testdata/vision/fist_landmarks.pbtxt) · [Upstream point](https://github.com/google-ai-edge/mediapipe/blob/238640e0ac3948b3b137451e25976640e8a78c1d/mediapipe/tasks/testdata/vision/pointing_up_landmarks.pbtxt) · [Upstream victory](https://github.com/google-ai-edge/mediapipe/blob/238640e0ac3948b3b137451e25976640e8a78c1d/mediapipe/tasks/testdata/vision/victory_landmarks.pbtxt)

### Unverified conditions

No physical webcam, interactive display, audio output, or labeled user-session collection was available. Preview rendering was exercised with synthetic keyboard events and a substituted display. Speech fallback paths were tested; pronunciation and audibility require listening. Pinch has synthetic geometry coverage only. Other hand shapes, fast motion, varied mobility, camera hardware, and Windows/macOS remain field tests.

## First webcam session

1. Start with default 2D geometry. Put both hands down, then hold Open Palm until a message appears. Keep holding for several seconds. Count duplicate messages. Briefly cover the hand and uncover it; then withdraw it fully and repeat. Record what the app does after each gap.
2. Try all five poses with each hand. Include finger configurations outside the vocabulary, edge-on palms, natural conversation at rest, and a second person entering the frame. Record the intended pose and observed label, including rejected poses. Undo an accidental message and check the transcript. If speech is enabled, listen to a complete phrase.
3. Record consented, constant-rate clips across at least two sessions with different distances, lighting and backgrounds. Annotate rest, pose onset, release and intended phrase independently of predictions. Keep the original recording private when appropriate. Save camera resolution, frame rate, model version, thresholds, hardware and software versions with each experiment.
4. Replay the same clips in all three modes. Compare the original four-PIP rule at commit `254eaa5` for its two named classes. Compare the current methods on the same five-class vocabulary and report results for the shared classes separately. Use development participants for threshold selection and different participants for final evaluation. Keep adjacent frames from a recording together.
5. Separate detector misses from wrong labels on detected hands. Publish a confusion matrix with Unknown and No hand, per-class precision/recall, macro-F1, and sample counts per person and gesture. At the event level, match one intended message to at most one confirmation inside its annotated interval. Count missing, wrong and duplicate messages, plus false messages per minute at rest. Report onset-to-confirmation median and 95th percentile for matched events alongside the miss rate.
6. For runtime, instrument capture, inference, classification, and display separately with a monotonic clock on the target laptop. Report warm-up conditions, processed frames/wall time, median and 95th-percentile durations. Use external synchronized observation if claiming physical motion-to-display latency. The practice countdown includes human reaction and configured hold time.
7. Ask intended users to choose comfortable poses and phrases, complete short communication tasks and correct mistakes. Measure completion, corrections and effort. Agree on acceptable false activations and response time with them before selecting settings.

Start with interpretable rules for distinct static poses. If held-out clips reveal persistent confusion, compare a lightweight landmark classifier on the same participant splits. Keep hold, release, correction and two-hand policies identical across experiments so changes in message quality can be attributed to the classifier.
