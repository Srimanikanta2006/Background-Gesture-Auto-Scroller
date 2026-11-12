"""
Ultra-Smooth & Slow Auto-Scroller Controller.
Sends gentle, micro-step scroll pulses tailored for comfortable reading.
"""

import time
import pyautogui

# Set minimal internal pause in pyautogui for fluid action
pyautogui.PAUSE = 0.005

class ScreenScroller:
    # Presets configured for reading comfort (negative values scroll down)
    SPEED_CONFIGS = {
        "Ultra Slow (Reading Speed - Recommended)": {
            "amount": -3,
            "interval": 0.08
        },
        "Slow (Comfortable Reading)": {
            "amount": -6,
            "interval": 0.06
        },
        "Normal (Glide)": {
            "amount": -15,
            "interval": 0.05
        },
        "Fast": {
            "amount": -35,
            "interval": 0.04
        }
    }

    def __init__(self, default_preset="Ultra Slow (Reading Speed - Recommended)"):
        self.current_preset = default_preset
        cfg = self.SPEED_CONFIGS.get(default_preset, self.SPEED_CONFIGS["Ultra Slow (Reading Speed - Recommended)"])
        self.scroll_amount = cfg["amount"]
        self.scroll_interval = cfg["interval"]
        self.is_enabled = True
        self.last_scroll_time = 0

    def set_speed(self, preset_name):
        if preset_name in self.SPEED_CONFIGS:
            self.current_preset = preset_name
            self.scroll_amount = self.SPEED_CONFIGS[preset_name]["amount"]
            self.scroll_interval = self.SPEED_CONFIGS[preset_name]["interval"]

    def toggle(self):
        self.is_enabled = not self.is_enabled
        return self.is_enabled

    def trigger_scroll(self):
        """Dispatches a single micro scroll pulse if the pacing interval has elapsed."""
        if not self.is_enabled:
            return

        now = time.time()
        if now - self.last_scroll_time >= self.scroll_interval:
            try:
                pyautogui.scroll(self.scroll_amount)
            except Exception:
                pass
            self.last_scroll_time = now
