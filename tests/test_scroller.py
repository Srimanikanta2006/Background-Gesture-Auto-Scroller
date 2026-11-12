import unittest
from engine.scroller import ScreenScroller

class TestScreenScroller(unittest.TestCase):
    def setUp(self):
        self.scroller = ScreenScroller()

    def test_default_configuration(self):
        self.assertIn("Ultra Slow", self.scroller.current_preset)
        self.assertLess(self.scroller.scroll_amount, 0)
        self.assertGreater(self.scroller.scroll_interval, 0.05)
        self.assertTrue(self.scroller.is_enabled)

    def test_speed_switching(self):
        for preset_name in ScreenScroller.SPEED_CONFIGS:
            self.scroller.set_speed(preset_name)
            self.assertEqual(self.scroller.current_preset, preset_name)
            self.assertEqual(self.scroller.scroll_amount, ScreenScroller.SPEED_CONFIGS[preset_name]["amount"])

    def test_toggle_state(self):
        state1 = self.scroller.toggle()
        self.assertFalse(state1)
        self.assertFalse(self.scroller.is_enabled)

        state2 = self.scroller.toggle()
        self.assertTrue(state2)
        self.assertTrue(self.scroller.is_enabled)

if __name__ == "__main__":
    unittest.main()
