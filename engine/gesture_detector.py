"""
High-Precision Gesture Detector using Google MediaPipe Hands.
Exclusively triggers for an unambiguous 2-finger (peace / read) gesture:
- Index and Middle fingers must be fully extended.
- Ring and Pinky fingers must be strictly curled/folded.
- Thumb must be folded (not pointing out).
- Closed palm / fist or open palm will NEVER trigger scrolling.
"""

import os
# Suppress C++ TensorFlow and MediaPipe stderr logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'

import cv2
import mediapipe as mp
import math

class GestureDetector:
    def __init__(self, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Consecutive frame confirmation: requires 3 solid matching frames
        self.required_consecutive_frames = 3
        self.consecutive_matches = 0

    @staticmethod
    def _dist(p1, p2):
        """Euclidean distance in 2D normalized coordinates."""
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def _is_finger_extended(self, landmarks, tip_i, dip_i, pip_i, mcp_i, wrist_i=0):
        """
        Mathematically verifies if a finger is extended vertically.
        Requires strict joint height order and knuckle-to-tip elongation.
        """
        tip = landmarks[tip_i]
        dip = landmarks[dip_i]
        pip = landmarks[pip_i]
        mcp = landmarks[mcp_i]
        wrist = landmarks[wrist_i]

        # 1. Height order: tip is highest, DIP next, PIP next, MCP lowest
        # Note: In screen coordinates, y=0 is TOP and y=1 is BOTTOM.
        # So smaller y means higher on the screen.
        if not (tip.y < dip.y < pip.y and tip.y < mcp.y):
            return False

        # 2. Length check: distance from MCP knuckle to TIP vs MCP to PIP
        d_tip_mcp = self._dist(tip, mcp)
        d_pip_mcp = self._dist(pip, mcp)
        if d_pip_mcp <= 0.0001:
            return False

        # Extended finger tip is ~1.7x - 2.5x the distance of PIP from MCP
        if (d_tip_mcp / d_pip_mcp) < 1.60:
            return False

        # 3. Distance from wrist: tip must be farther from wrist than PIP
        if self._dist(tip, wrist) < self._dist(pip, wrist) * 1.15:
            return False

        return True

    def _is_finger_curled(self, landmarks, tip_i, dip_i, pip_i, mcp_i, wrist_i=0):
        """
        Mathematically verifies if a finger is folded or curled into the palm (fist/closed).
        """
        tip = landmarks[tip_i]
        dip = landmarks[dip_i]
        pip = landmarks[pip_i]
        mcp = landmarks[mcp_i]
        wrist = landmarks[wrist_i]

        # If tip is lower than PIP or DIP, it is folded downwards
        if tip.y > pip.y or tip.y > dip.y:
            return True

        # In a closed fist/palm, tip is tucked close to the base knuckle
        d_tip_mcp = self._dist(tip, mcp)
        d_pip_mcp = self._dist(pip, mcp)
        if d_pip_mcp > 0.0001 and (d_tip_mcp / d_pip_mcp) < 1.25:
            return True

        # If tip is closer to the wrist than PIP
        if self._dist(tip, wrist) <= self._dist(pip, wrist) * 1.05:
            return True

        return False

    def evaluate_hand(self, landmarks):
        """
        Evaluates the exact hand pose.
        Returns:
            is_valid_peace (bool): True ONLY if exactly Index & Middle are extended.
            debug_info (dict): Detailed status of all fingers for preview display.
        """
        # Finger indices: (TIP, DIP, PIP, MCP)
        # Index: 8, 7, 6, 5
        index_up = self._is_finger_extended(landmarks, 8, 7, 6, 5)
        # Middle: 12, 11, 10, 9
        middle_up = self._is_finger_extended(landmarks, 12, 11, 10, 9)
        # Ring: 16, 15, 14, 13
        ring_folded = self._is_finger_curled(landmarks, 16, 15, 14, 13)
        # Pinky: 20, 19, 18, 17
        pinky_folded = self._is_finger_curled(landmarks, 20, 19, 18, 17)

        # Thumb: 4 (TIP), 3 (IP), 2 (MCP)
        # When thumb is folded against palm, it is close to middle MCP (9) or below index PIP (6)
        thumb_tip = landmarks[4]
        thumb_mcp = landmarks[2]
        middle_mcp = landmarks[9]
        index_pip = landmarks[6]

        thumb_folded = (
            (self._dist(thumb_tip, middle_mcp) < self._dist(thumb_mcp, middle_mcp) * 1.35) or
            (thumb_tip.y > index_pip.y)
        )

        # Height clearance: Index and Middle tips must be distinctly higher than Ring & Pinky
        tips_clearance = (
            landmarks[8].y < landmarks[16].y - 0.06 and
            landmarks[12].y < landmarks[16].y - 0.06 and
            landmarks[8].y < landmarks[20].y - 0.06 and
            landmarks[12].y < landmarks[20].y - 0.06
        )

        is_valid_peace = (
            index_up and
            middle_up and
            ring_folded and
            pinky_folded and
            thumb_folded and
            tips_clearance
        )

        debug_info = {
            "index_up": index_up,
            "middle_up": middle_up,
            "ring_folded": ring_folded,
            "pinky_folded": pinky_folded,
            "thumb_folded": thumb_folded,
            "tips_clearance": tips_clearance,
            "is_valid": is_valid_peace
        }
        return is_valid_peace, debug_info

    def process_frame(self, frame, draw_preview=False):
        """
        Process a single BGR frame.
        Returns:
            should_scroll (bool): True if 2 fingers are stably held.
            annotated_frame (ndarray or None): Frame with visual feedback if draw_preview=True.
        """
        flipped = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        gesture_detected = False
        annotated_frame = flipped if draw_preview else None
        debug_status = "No Hand Detected"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if draw_preview and annotated_frame is not None:
                    self.mp_draw.draw_landmarks(
                        annotated_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )

                is_peace, info = self.evaluate_hand(hand_landmarks.landmark)

                if is_peace:
                    gesture_detected = True
                    debug_status = "2 Fingers (Peace) -> SCROLLING"
                else:
                    # Provide informative diagnosis for preview
                    if not info["index_up"] and not info["middle_up"]:
                        debug_status = "Closed Palm / Fist -> IDLE"
                    elif not info["ring_folded"] or not info["pinky_folded"]:
                        debug_status = "Open Palm (Too many fingers) -> IDLE"
                    elif not info["middle_up"]:
                        debug_status = "1 Finger Only -> IDLE"
                    elif not info["thumb_folded"]:
                        debug_status = "Thumb extended -> IDLE"
                    else:
                        debug_status = "Adjust Hand Position -> IDLE"
                break

        # Fast drop: If hand is closed or folded, reset immediately with no lag
        if gesture_detected:
            self.consecutive_matches += 1
        else:
            self.consecutive_matches = 0  # Instant stop on palm close!

        should_scroll = self.consecutive_matches >= self.required_consecutive_frames

        if draw_preview and annotated_frame is not None:
            # Draw real-time state badge
            color = (0, 255, 0) if should_scroll else (0, 165, 255)
            cv2.rectangle(annotated_frame, (10, 10), (580, 55), (20, 20, 20), -1)
            cv2.putText(annotated_frame, debug_status, (20, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

        return should_scroll, annotated_frame

    def close(self):
        self.hands.close()
