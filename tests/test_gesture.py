import unittest
from engine.gesture_detector import GestureDetector

class MockLandmark:
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z

class TestGestureDetector(unittest.TestCase):
    def setUp(self):
        self.detector = GestureDetector()

    def tearDown(self):
        self.detector.close()

    def _build_fist_landmarks(self):
        # 21 points where all fingers are curled towards palm
        points = [MockLandmark(0.5, 0.8) for _ in range(21)]
        # Knuckles (MCP)
        for idx in [1, 2, 5, 9, 13, 17]:
            points[idx] = MockLandmark(0.5, 0.6)
        # PIP joints
        for idx in [3, 6, 10, 14, 18]:
            points[idx] = MockLandmark(0.5, 0.55)
        # DIP joints
        for idx in [7, 11, 15, 19]:
            points[idx] = MockLandmark(0.5, 0.60)
        # Tips curled back down
        for idx in [4, 8, 12, 16, 20]:
            points[idx] = MockLandmark(0.5, 0.65)
        return points

    def test_closed_palm_does_not_trigger(self):
        fist = self._build_fist_landmarks()
        is_peace, info = self.detector.evaluate_hand(fist)
        self.assertFalse(is_peace, "Closed palm / fist must not trigger scroll")

    def test_exact_two_fingers_triggers(self):
        hand = self._build_fist_landmarks()
        # Straighten Index finger
        hand[5] = MockLandmark(0.45, 0.60)  # MCP
        hand[6] = MockLandmark(0.45, 0.45)  # PIP
        hand[7] = MockLandmark(0.45, 0.35)  # DIP
        hand[8] = MockLandmark(0.45, 0.20)  # TIP

        # Straighten Middle finger
        hand[9] = MockLandmark(0.55, 0.60)   # MCP
        hand[10] = MockLandmark(0.55, 0.45)  # PIP
        hand[11] = MockLandmark(0.55, 0.35)  # DIP
        hand[12] = MockLandmark(0.55, 0.18)  # TIP

        # Ring, Pinky, and Thumb remain curled in fist
        hand[4] = MockLandmark(0.52, 0.62)

        is_peace, info = self.detector.evaluate_hand(hand)
        self.assertTrue(is_peace, "Strict 2-finger sign must trigger scroll")

    def test_open_palm_does_not_trigger(self):
        hand = self._build_fist_landmarks()
        # Extend all fingers
        for tip, dip, pip, mcp in [(8, 7, 6, 5), (12, 11, 10, 9), (16, 15, 14, 13), (20, 19, 18, 17)]:
            hand[mcp] = MockLandmark(0.5, 0.60)
            hand[pip] = MockLandmark(0.5, 0.45)
            hand[dip] = MockLandmark(0.5, 0.35)
            hand[tip] = MockLandmark(0.5, 0.20)

        is_peace, info = self.detector.evaluate_hand(hand)
        self.assertFalse(is_peace, "Open palm with all fingers must not trigger scroll")

if __name__ == "__main__":
    unittest.main()

