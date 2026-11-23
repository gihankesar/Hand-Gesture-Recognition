# Learning log

## 1. From finger count to anatomical features

**Change and reason.** The original dot-product angle, index base and distal angles, thumb IP angle, thumb direction, and palm-normalized pinch distance are retained in `gesture/geometry.py`. Floating-point coordinates preserve small movements lost to pixel rounding. The four long fingers now each have a PIP and DIP angle. Keeping identity lets an index point differ from a fist even when only one finger is straight.

**Mathematics and operation.** At joint B, normalize A−B and C−B, clip their dot product to [−1,1], then apply arccos and convert to degrees. Straight bones give approximately 180°. Translate by the wrist and divide lengths by the index-to-little MCP span. Translation and uniform scaling cancel. The thumb IP angle describes extension, its palm-relative direction and tip-to-middle-MCP reach describe posture, and its tip-to-index gap approximates opposition. Distances cannot prove physical contact. Invalid segments or an extremely narrow projected palm reject the entire feature vector. This deliberately trades coverage for fewer accidental messages.

**Decision rule.** A straight finger requires both joints above or at the straight threshold. A curled finger requires its PIP at or below the curled threshold. The gap between thresholds allows abstention. Pinch gets priority and requires at least two extended non-index fingers. Fist also constrains thumb reach. V Sign requires tip spread. The numbers are engineering starting points. Printing a feature does not establish its predictive power.

**Evidence and next study.** Unit tests exercise 0°, 90°, 180°, invalid inputs, palm normalization, reflection, all labels and boundary cases. The original application also passed a blank-frame and two-open-palms smoke check before refactoring. Study projection versus Euclidean angles, the MediaPipe landmark index chart, and how a confusion matrix changes as thresholds move. Try the same tilted pose in each geometry mode before choosing a threshold.

## 2. From frame labels to messages

**Change and reason.** A new confirmation state machine consumes the list of labels and a monotonic millisecond timestamp. A message must represent an intentional hold. A single video frame is weak evidence, and consecutive video frames are correlated.

**Algorithm and operation.** A change of candidate restarts a stopwatch. Only an uninterrupted single recognized label can reach the hold duration. Emission latches the output until continuous observed absence reaches the release duration. An unknown pose or a second hand interrupts a pending hold and preserves any existing latch. A frame gap above the configured limit breaks accumulated evidence. This design lets two people enter the picture without a detection-list index switching speakers mid-hold when both are visible. It cannot identify a person silently replacing another between sampled frames. A hand temporarily lost for the entire release duration is indistinguishable from intentional withdrawal.

**Verification and study.** Timestamped unit sequences cover exact boundaries, brief and prolonged absence, a second hand, a stalled camera, and repeating a gesture after release. Tests check both the emitted events and transcript correction. Study finite-state machines, signal debouncing, and the difference between per-frame accuracy and duplicate messages per minute. Trace a hold, a 100 ms dropout and a return on paper.
