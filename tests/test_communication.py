import unittest

from gesture.communication import Confirmation, Transcript


class CommunicationTests(unittest.TestCase):
    def setUp(self):
        self.c = Confirmation(hold_ms=200, release_ms=100, max_gap_ms=150)

    def feed(self, steps):
        events = []
        for timestamp, labels in steps:
            event = self.c.update(labels, timestamp)
            if event:
                events.append(event)
        return events

    def test_hold_release_repeat(self):
        palm = ["Open Palm"]
        result = self.feed([(0, palm), (100, palm), (199, palm), (200, palm),
                            (300, palm), (400, []), (499, []), (500, palm),
                            (600, palm), (700, []), (800, []), (900, palm),
                            (1000, palm), (1100, palm)])
        self.assertEqual(result, ["Open Palm", "Open Palm"])

    def test_multihand_and_unknown_restart_hold(self):
        fist = ["Fist"]
        self.assertEqual(self.feed([(0, fist), (150, fist), (170, fist*2),
                                    (200, fist), (310, ["Unknown"]), (320, fist),
                                    (400, fist), (520, fist)]), ["Fist"])
        self.assertEqual(self.feed([(610, ["Unknown"]), (730, ["Unknown"]),
                                    (750, fist*2), (800, fist), (900, fist),
                                    (1000, fist)]), [])

    def test_stall_cannot_confirm_or_rearm(self):
        fist = ["Fist"]
        self.assertEqual(self.feed([(0, fist), (1000, fist)]), [])
        self.assertEqual(self.feed([(1100, fist), (1200, fist)]), ["Fist"])
        self.assertEqual(self.feed([(1300, []), (2000, []), (2001, fist),
                                    (2120, fist), (2250, fist)]), [])

    def test_missing_and_invalid_evidence(self):
        self.assertEqual(self.feed([(0, []), (120, ["Unknown"]), (250, ["Point"]),
                                    (380, []), (500, ["Point"]), (620, ["Point"])]), [])
        with self.assertRaises(ValueError):
            self.c.update([], 100)
        with self.assertRaises(ValueError):
            Confirmation(hold_ms=0)

    def test_edit_text(self):
        t = Transcript()
        t.undo()
        self.assertEqual(t.confirm("Point"), "Look there.")
        t.confirm("Fist")
        t.undo()
        self.assertEqual(t.messages, ["Look there."])
        t.clear()
        self.assertEqual(t.messages, [])
