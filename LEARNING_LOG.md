# Learning log

## 1. From finger count to anatomical features

**Change and reason.** The original dot-product angle, index base and distal angles, thumb IP angle, thumb direction, and palm-normalized pinch distance are retained in `gesture/geometry.py`. Floating-point coordinates preserve small movements lost to pixel rounding. The four long fingers now each have a PIP and DIP angle. Keeping identity lets an index point differ from a fist even when only one finger is straight.

**Mathematics and operation.** At joint B, normalize A−B and C−B, clip their dot product to [−1,1], then apply arccos and convert to degrees. Straight bones give approximately 180°. Translate by the wrist and divide lengths by the index-to-little MCP span. Translation and uniform scaling cancel. The thumb IP angle describes extension, its palm-relative direction and tip-to-middle-MCP reach describe posture, and its tip-to-index gap approximates opposition. Distances cannot prove physical contact. Invalid segments or an extremely narrow projected palm reject the entire feature vector. This deliberately trades coverage for fewer accidental messages.

**Decision rule.** A straight finger requires both joints above or at the straight threshold. A curled finger requires its PIP at or below the curled threshold. The gap between thresholds allows abstention. Pinch gets priority and requires at least two extended non-index fingers. Fist also constrains thumb reach. V Sign requires tip spread. The numbers are engineering starting points. Printing a feature does not establish its predictive power.

**Evidence and next study.** Unit tests exercise 0°, 90°, 180°, invalid inputs, palm normalization, reflection, all labels and boundary cases. The original application also passed a blank-frame and two-open-palms smoke check before refactoring. Study projection versus Euclidean angles, the MediaPipe landmark index chart, and how a confusion matrix changes as thresholds move. Try the same tilted pose in each geometry mode before choosing a threshold.
