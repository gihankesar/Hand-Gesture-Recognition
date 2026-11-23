from dataclasses import replace
import unittest

import numpy as np

from gesture.geometry import Features, calculate_angle, extract, image_points
from gesture.rules import Thresholds, classify
from types import SimpleNamespace


class GeometryTests(unittest.TestCase):
    def test_angles(self):
        for end, expected in [((2, 0), 180), ((1, 2), 90), ((0, 0), 0)]:
            self.assertAlmostEqual(calculate_angle((0, 0), (1, 0), end), expected)
        self.assertAlmostEqual(calculate_angle((1, 0, 0), (0, 0, 0), (0, 0, 1)), 90)
        self.assertIsNone(calculate_angle((0, 0), (0, 0), (1, 0)))
        self.assertIsNone(calculate_angle(None, (0, 0), (1, 0)))

    def test_hand_geometry(self):
        # Synthetic open palm with four parallel straight fingers.
        p = [(0, -1), (-1.2, -.5), (-1.5, 0), (-2, .2), (-2.5, .4)]
        for x in [-1, 0, .6, 1]:
            p.extend((x, y) for y in [0, .6, 1, 1.3])
        p = np.asarray(p)
        f = extract(p)
        self.assertEqual(classify(f), "Open Palm")
        self.assertAlmostEqual(f.thumb_index_gap, np.linalg.norm(p[4]-p[8])/2)
        for coords in [p*3 + 4, p*[-1, 1], np.column_stack([p, np.zeros(21)])]:
            self.assertTrue(np.allclose(extract(coords).pip, f.pip))
            self.assertAlmostEqual(extract(coords).spread, f.spread)
        for target, source in [(17, 5), (3, 2), (7, 6), (9, 0)]:
            bad = p.copy()
            bad[target] = bad[source]
            self.assertIsNone(extract(bad))

    def test_projection(self):
        p = [SimpleNamespace(x=.5, y=.25, z=-.1)]
        self.assertEqual(image_points(p, 640, 480), [(320, 120)])
        self.assertEqual(image_points(p, 640, 480, True), [(320, 120, -64)])

    def test_invalid(self):
        for data in [None, [], [[1]], np.zeros((21, 3)), np.full((21, 2), np.nan),
                     np.arange(42).reshape(21, 2)]:
            self.assertEqual(classify(extract(data)), "Unknown")


class RulesTests(unittest.TestCase):
    def pose(self, pip, **changes):
        features = Features(tuple(pip), (180,)*4, 140, 160, 70, .7, .7, .5)
        return replace(features, **changes)

    def test_vocabulary_and_ambiguity(self):
        for angles, label in [([170]*4, "Open Palm"), ([100]*4, "Fist"),
                              ([170, 90, 90, 90], "Point"), ([170, 170, 90, 90], "V Sign"),
                              ([90, 170, 90, 90], "Unknown"), ([135]*4, "Unknown")]:
            self.assertEqual(classify(self.pose(angles)), label)
        self.assertEqual(classify(self.pose([100, 170, 170, 170], thumb_index_gap=.22)), "Pinch")
        self.assertEqual(classify(self.pose([90]*4, thumb_palm_gap=1.2)), "Unknown")

    def test_boundaries(self):
        self.assertEqual(classify(self.pose([155, 115, 115, 115])), "Point")
        self.assertEqual(classify(self.pose([154.99, 115, 115, 115])), "Unknown")
        self.assertEqual(classify(self.pose([155, 115.01, 115, 115])), "Unknown")
        self.assertEqual(classify(self.pose([160, 160, 90, 90], spread=.39)), "Unknown")
        self.assertEqual(classify(self.pose([160, 160, 90, 90]), Thresholds(straight=165)), "Unknown")
        with self.assertRaises(ValueError):
            Thresholds(curled=170)
