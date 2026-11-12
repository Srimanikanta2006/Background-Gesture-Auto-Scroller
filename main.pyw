"""
Invisible Background Gesture Scroller with System Tray Controller.
Runs quietly in the background without any visible terminal or camera window.
100% Offline & Private: No camera images or telemetry are ever stored or transmitted.
"""

import os
# Suppress C++ TensorFlow and MediaPipe stderr logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'

import sys
import time
import atexit
import ctypes
import threading
import cv2
from PIL import Image, ImageDraw
import pystray
import pyautogui

from engine.gesture_detector import GestureDetector
from engine.scroller import ScreenScroller

# Enable PyAutoGUI safety fail-safe (moving cursor to any screen corner halts actions)
pyautogui.FAILSAFE = True


def acquire_single_instance_mutex():
    """
    Ensures only a single instance of Gesture Scroller runs at any time.
    Uses native Windows named mutex.
    """
    mutex_name = "Local\\BackgroundGestureScrollerSingleInstanceMutex"
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    last_error = kernel32.GetLastError()
    ERROR_ALREADY_EXISTS = 183
    if last_error == ERROR_ALREADY_EXISTS:
        # Another instance is already running
        sys.exit(0)
    return mutex


class BackgroundGestureApp:
    def __init__(self):
        self.detector = GestureDetector()
        self.scroller = ScreenScroller(default_preset="Ultra Slow (Reading Speed - Recommended)")
        self.running = True
        self.is_active = True
        self.show_preview = False

        self.cap = None
        self.tray_icon = None
        self.worker_thread = None

        atexit.register(self.cleanup)

    def create_icon_image(self, active=True):
        """Generates a dynamic 64x64 system tray icon."""
        width = 64
        height = 64
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Background circular badge
        bg_color = (30, 41, 59) if active else (71, 85, 105)
        draw.ellipse((4, 4, 60, 60), fill=bg_color)

        # Two vertical pill bars representing the 2 fingers (peace / read sign)
        finger_color = (56, 189, 248) if active else (148, 163, 184)
        draw.rounded_rectangle((22, 14, 30, 44), radius=4, fill=finger_color)
        draw.rounded_rectangle((34, 14, 42, 44), radius=4, fill=finger_color)

        # Status indicator dot in bottom-right
        indicator_color = (34, 197, 94) if active else (239, 68, 68)
        draw.ellipse((44, 44, 58, 58), fill=indicator_color)

        return image

    def camera_loop(self):
        """Background worker capturing webcam frames silently with resilient error recovery."""
        camera_failures = 0

        while self.running:
            if not self.is_active:
                time.sleep(0.1)
                continue

            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                if not self.cap.isOpened():
                    camera_failures += 1
                    # Sleep longer if camera is occupied or disconnected to prevent CPU spin
                    time.sleep(min(2.0, 0.5 * camera_failures))
                    continue
                else:
                    camera_failures = 0

            success, frame = self.cap.read()
            if not success:
                camera_failures += 1
                if camera_failures > 5 and self.cap:
                    self.cap.release()
                    self.cap = None
                time.sleep(0.1)
                continue
            else:
                camera_failures = 0

            # Process frame for 2-finger gesture
            draw_preview = self.show_preview
            should_scroll, annotated_frame = self.detector.process_frame(frame, draw_preview=draw_preview)

            if should_scroll:
                self.scroller.trigger_scroll()

            # Handle calibration preview window if requested from tray
            if self.show_preview and annotated_frame is not None:
                cv2.putText(annotated_frame, "Press 'Q' to close test view", (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                cv2.imshow("Gesture Scroller - Camera Test", annotated_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or cv2.getWindowProperty("Gesture Scroller - Camera Test", cv2.WND_PROP_VISIBLE) < 1:
                    self.show_preview = False
                    cv2.destroyAllWindows()
            elif not self.show_preview:
                try:
                    if cv2.getWindowProperty("Gesture Scroller - Camera Test", cv2.WND_PROP_VISIBLE) >= 0:
                        cv2.destroyAllWindows()
                except Exception:
                    pass

            # Micro-pause to maintain low CPU profile (~1-2%)
            time.sleep(0.015)

        self.cleanup()

    def toggle_active(self, icon, item):
        self.is_active = not self.is_active
        self.scroller.is_enabled = self.is_active
        icon.icon = self.create_icon_image(self.is_active)

    def set_speed(self, speed_name):
        def handler(icon, item):
            self.scroller.set_speed(speed_name)
        return handler

    def toggle_preview(self, icon, item):
        self.show_preview = not self.show_preview
        if not self.show_preview:
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass

    def cleanup(self):
        """Releases camera and OpenCV resources cleanly."""
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
        try:
            self.detector.close()
            cv2.destroyAllWindows()
        except Exception:
            pass

    def exit_app(self, icon, item):
        self.running = False
        if icon:
            icon.stop()
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)
        self.cleanup()
        sys.exit(0)

    def build_menu(self):
        speed_items = []
        for name in ScreenScroller.SPEED_CONFIGS.keys():
            speed_items.append(
                pystray.MenuItem(
                    name,
                    self.set_speed(name),
                    checked=lambda item, n=name: self.scroller.current_preset == n,
                    radio=True
                )
            )

        return pystray.Menu(
            pystray.MenuItem(
                lambda text: "Pause Detection" if self.is_active else "Resume Detection",
                self.toggle_active
            ),
            pystray.MenuItem("Scroll Speed", pystray.Menu(*speed_items)),
            pystray.MenuItem(
                lambda text: "Hide Camera Test" if self.show_preview else "Show Camera Test (Preview)",
                self.toggle_preview
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit Gesture Scroller", self.exit_app)
        )

    def run(self):
        self.worker_thread = threading.Thread(target=self.camera_loop, daemon=True)
        self.worker_thread.start()

        initial_image = self.create_icon_image(active=True)
        self.tray_icon = pystray.Icon(
            "GestureScroller",
            initial_image,
            "Gesture Auto-Scroller (2 Fingers to Scroll)",
            menu=self.build_menu()
        )
        self.tray_icon.run()


if __name__ == "__main__":
    _instance_mutex = acquire_single_instance_mutex()
    app = BackgroundGestureApp()
    app.run()
