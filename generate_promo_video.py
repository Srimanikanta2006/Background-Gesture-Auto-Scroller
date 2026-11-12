"""
Commercial / Ad-Style Promo Video and GIF Generator
Renders a high-resolution, sleek visual animation demonstrating:
1. Long ChatGPT reading fatigue
2. The 2-finger hand gesture detection with glowing MediaPipe skeleton
3. Smooth line-by-line auto-scrolling
4. Immediate freeze upon closing palm/fist
5. 100% background system tray execution
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

# Video specifications
WIDTH = 800
HEIGHT = 480
FPS = 20
TOTAL_FRAMES = 210  # ~10.5 seconds of high-impact ad walkthrough

# Try loading Segoe UI or fallback to default
FONT_PATH = "C:\\Windows\\Fonts\\segoeui.ttf"
FONT_BOLD_PATH = "C:\\Windows\\Fonts\\segoeuib.ttf"

def get_font(size, bold=False):
    path = FONT_BOLD_PATH if bold else FONT_PATH
    if os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

font_title = get_font(20, bold=True)
font_sub = get_font(13, bold=False)
font_h1 = get_font(16, bold=True)
font_body = get_font(12, bold=False)
font_badge = get_font(12, bold=True)
font_alert = get_font(14, bold=True)
font_caption = get_font(15, bold=True)

# Fake ChatGPT response paragraphs
CHATGPT_PARAGRAPHS = [
    "Deep Learning & Attention Mechanisms:",
    "Large language models rely on multi-head attention",
    "to compute rich token representations across long contexts.",
    "Unlike traditional recurrent networks, transformers process",
    "entire sequences in parallel, enabling rapid scaling.",
    "--------------------------------------------------",
    "Key Architectural Components:",
    "1. Self-Attention Layer: Queries, Keys, and Values",
    "2. Feed-Forward Networks with Non-Linear Activations",
    "3. Positional Encodings: Rotary & Sinusoidal Embeddings",
    "4. Layer Normalization & Residual Skip Connections",
    "--------------------------------------------------",
    "Why Hands-Free Reading Matters:",
    "When reading dense technical explanations or code breakdowns,",
    "manually clicking and scrolling constantly breaks focus.",
    "With Background Gesture Auto-Scroller, your eyes stay on the text",
    "as it smoothly glides line-by-line at your natural reading pace.",
    "--------------------------------------------------",
    "Privacy & Zero-Lag Offline Processing:",
    "All hand landmarks are processed 100% locally on your CPU.",
    "No web requests, no cloud uploads, completely secure.",
    "Stop anytime by closing your hand into a relaxed palm."
]

def draw_hand_skeleton(draw, center_x, center_y, peace_ratio, is_peace):
    """
    Interpolates hand skeleton between Fist (peace_ratio=0.0) and Peace (peace_ratio=1.0).
    Draws MediaPipe-like joints and glowing connections.
    """
    wrist = (center_x, center_y + 65)

    # Base knuckles (MCPs)
    mcp_index = (center_x - 18, center_y + 15)
    mcp_middle = (center_x - 3, center_y + 10)
    mcp_ring = (center_x + 12, center_y + 15)
    mcp_pinky = (center_x + 25, center_y + 22)
    mcp_thumb = (center_x - 28, center_y + 35)

    # Interpolate Index Tip & Middle Tip
    # Fist pos vs Extended Peace pos
    tip_index_fist = (center_x - 16, center_y + 25)
    tip_index_peace = (center_x - 22, center_y - 48)

    tip_middle_fist = (center_x - 3, center_y + 20)
    tip_middle_peace = (center_x + 4, center_y - 52)

    # Calculate actual tip positions based on peace_ratio
    tip_index = (
        int(tip_index_fist[0] + (tip_index_peace[0] - tip_index_fist[0]) * peace_ratio),
        int(tip_index_fist[1] + (tip_index_peace[1] - tip_index_fist[1]) * peace_ratio)
    )
    pip_index = (
        int(mcp_index[0] + (tip_index[0] - mcp_index[0]) * 0.5),
        int(mcp_index[1] + (tip_index[1] - mcp_index[1]) * 0.5)
    )

    tip_middle = (
        int(tip_middle_fist[0] + (tip_middle_peace[0] - tip_middle_fist[0]) * peace_ratio),
        int(tip_middle_fist[1] + (tip_middle_peace[1] - tip_middle_fist[1]) * peace_ratio)
    )
    pip_middle = (
        int(mcp_middle[0] + (tip_middle[0] - mcp_middle[0]) * 0.5),
        int(mcp_middle[1] + (tip_middle[1] - mcp_middle[1]) * 0.5)
    )

    # Ring, Pinky, and Thumb remain folded in palm
    tip_ring = (center_x + 12, center_y + 28)
    tip_pinky = (center_x + 24, center_y + 32)
    tip_thumb = (center_x - 12, center_y + 36)

    # Colors: bright neon green if peace, cyan/blue if transitioning, muted gray-cyan if fist
    if is_peace:
        line_color = (34, 197, 94)      # Emerald green
        joint_color = (74, 222, 128)
    elif peace_ratio > 0.3:
        line_color = (56, 189, 248)     # Sky blue
        joint_color = (125, 211, 252)
    else:
        line_color = (100, 116, 139)    # Slate
        joint_color = (148, 163, 184)

    # Draw palm webbing
    draw.polygon([wrist, mcp_thumb, mcp_index, mcp_middle, mcp_ring, mcp_pinky], fill=(20, 27, 38))

    # Draw bone lines
    def draw_bone(p1, p2, width=3):
        draw.line([p1, p2], fill=line_color, width=width)

    # Connect palm bones
    draw_bone(wrist, mcp_thumb)
    draw_bone(wrist, mcp_index)
    draw_bone(wrist, mcp_middle)
    draw_bone(wrist, mcp_ring)
    draw_bone(wrist, mcp_pinky)

    draw_bone(mcp_thumb, tip_thumb)
    draw_bone(mcp_index, pip_index)
    draw_bone(pip_index, tip_index)
    draw_bone(mcp_middle, pip_middle)
    draw_bone(pip_middle, tip_middle)
    draw_bone(mcp_ring, tip_ring)
    draw_bone(mcp_pinky, tip_pinky)

    # Draw joint dots
    all_joints = [wrist, mcp_thumb, mcp_index, mcp_middle, mcp_ring, mcp_pinky,
                  tip_thumb, pip_index, tip_index, pip_middle, tip_middle, tip_ring, tip_pinky]
    for j in all_joints:
        r = 3
        draw.ellipse((j[0] - r, j[1] - r, j[0] + r, j[1] + r), fill=joint_color)

    # Highlight index and middle tips if peace
    if is_peace:
        for t in [tip_index, tip_middle]:
            draw.ellipse((t[0] - 6, t[1] - 6, t[0] + 6, t[1] + 6), outline=(34, 197, 94), width=2)


def render_frame(frame_num):
    # Main dark canvas
    img = Image.new("RGB", (WIDTH, HEIGHT), (13, 17, 23))
    draw = ImageDraw.Draw(img)

    # --- 1. Top Header Bar ---
    draw.rectangle((0, 0, WIDTH, 54), fill=(22, 27, 34))
    draw.line((0, 54, WIDTH, 54), fill=(48, 54, 61), width=1)

    # App icon badge
    draw.rounded_rectangle((18, 12, 48, 42), radius=6, fill=(30, 41, 59))
    draw.rounded_rectangle((28, 18, 32, 36), radius=2, fill=(56, 189, 248))
    draw.rounded_rectangle((34, 18, 38, 36), radius=2, fill=(56, 189, 248))

    draw.text((58, 12), "Background Gesture Auto-Scroller", fill=(240, 246, 252), font=font_title)
    draw.text((60, 34), "Hands-Free Reading for ChatGPT & Articles", fill=(139, 148, 158), font=font_sub)

    # Offline Pill Badge
    draw.rounded_rectangle((650, 14, 780, 40), radius=13, fill=(33, 38, 45), outline=(56, 189, 248))
    draw.ellipse((662, 24, 670, 32), fill=(34, 197, 94))
    draw.text((678, 20), "100% OFFLINE", fill=(240, 246, 252), font=font_badge)

    # --- 2. Determine Timeline Phase & States ---
    # Phase 1 (0..35): Palm closed, text static
    # Phase 2 (36..55): Fingers rising to peace sign
    # Phase 3 (56..145): Peace held, active smooth auto-scroll
    # Phase 4 (146..180): Palm closes into fist, scrolling halts
    # Phase 5 (181..210): Summary / Outro callout

    scroll_y = 0
    peace_ratio = 0.0
    is_peace = False
    caption_text = ""
    caption_color = (255, 255, 255)
    status_label = "IDLE (Hand Closed)"
    status_color = (139, 148, 158)

    if frame_num <= 35:
        peace_ratio = 0.0
        is_peace = False
        scroll_y = 0
        caption_text = "Tired of constantly scrolling long ChatGPT answers?"
        caption_color = (248, 113, 113) # Red/coral
        status_label = "IDLE - Hand Closed (Zero Scroll)"
        status_color = (148, 163, 184)

    elif 35 < frame_num <= 55:
        t = (frame_num - 35) / 20.0
        peace_ratio = t
        is_peace = (peace_ratio > 0.85)
        scroll_y = 0
        caption_text = "✌ Just show 2 fingers to your webcam!"
        caption_color = (56, 189, 248) # Cyan
        status_label = "Detecting 2 Fingers..." if not is_peace else "LOCKED: 2 Fingers (Peace)"
        status_color = (56, 189, 248) if not is_peace else (34, 197, 94)

    elif 55 < frame_num <= 145:
        peace_ratio = 1.0
        is_peace = True
        # Smooth scroll distance
        scroll_y = int((frame_num - 55) * 1.5)
        caption_text = "Auto-scrolling activated! Glides smoothly at reading speed."
        caption_color = (74, 222, 128) # Green
        status_label = "● SCROLLING ACTIVE (Line by Line)"
        status_color = (34, 197, 94)

    elif 145 < frame_num <= 180:
        t = max(0.0, 1.0 - (frame_num - 145) / 12.0)
        peace_ratio = t
        is_peace = False
        scroll_y = int((145 - 55) * 1.5) # Freeze exactly where it stopped!
        caption_text = "Close your hand into a palm/fist -> Instantly stops!"
        caption_color = (251, 191, 36) # Amber
        status_label = "STOPPED (Closed Palm Detected)"
        status_color = (251, 191, 36)

    else:
        peace_ratio = 0.0
        is_peace = False
        scroll_y = int((145 - 55) * 1.5)
        caption_text = "Runs silently in Windows Tray • 100% Free • Zero CPU Lag"
        caption_color = (192, 132, 252) # Purple
        status_label = "Minimized to System Tray"
        status_color = (192, 132, 252)

    # --- 3. Left Panel: ChatGPT Browser Window Mockup ---
    bx, by, bw, bh = 20, 68, 440, 340
    # Window card background
    draw.rounded_rectangle((bx, by, bx + bw, by + bh), radius=8, fill=(22, 27, 34), outline=(48, 54, 61))

    # Browser tab header
    draw.rounded_rectangle((bx, by, bx + bw, by + 32), radius=8, fill=(33, 38, 45))
    # Red, yellow, green window buttons
    draw.ellipse((bx + 12, by + 11, bx + 22, by + 21), fill=(239, 68, 68))
    draw.ellipse((bx + 28, by + 11, bx + 38, by + 21), fill=(245, 158, 11))
    draw.ellipse((bx + 44, by + 11, bx + 54, by + 21), fill=(34, 197, 94))

    # Address bar
    draw.rounded_rectangle((bx + 75, by + 6, bx + bw - 20, by + 26), radius=5, fill=(13, 17, 23))
    draw.text((bx + 85, by + 9), "🔒 https://chatgpt.com/c/research-digest", fill=(139, 148, 158), font=font_body)

    # ChatGPT Content Area (Clipped inside)
    # Create child image for clipping text scroll
    content_w = bw - 24
    content_h = bh - 48
    content_img = Image.new("RGB", (content_w, content_h), (22, 27, 34))
    c_draw = ImageDraw.Draw(content_img)

    # Render paragraphs with scroll_y offset
    line_y = 10 - scroll_y
    for p in CHATGPT_PARAGRAPHS:
        if p.startswith("Deep Learning") or p.startswith("Key Arch") or p.startswith("Why Hands") or p.startswith("Privacy"):
            c_draw.text((10, line_y), p, fill=(56, 189, 248), font=font_h1)
            line_y += 24
        elif p.startswith("---"):
            c_draw.line((10, line_y + 4, content_w - 20, line_y + 4), fill=(48, 54, 61), width=1)
            line_y += 14
        else:
            c_draw.text((10, line_y), p, fill=(201, 209, 217), font=font_body)
            line_y += 18

    # Paste clipped content
    img.paste(content_img, (bx + 12, by + 38))

    # Scrollbar Track & Thumb
    sb_x = bx + bw - 10
    sb_y = by + 40
    sb_h = bh - 50
    draw.rectangle((sb_x, sb_y, sb_x + 4, sb_y + sb_h), fill=(33, 38, 45))
    thumb_h = 45
    max_thumb_travel = sb_h - thumb_h
    # Progress ratio: scroll_y max is ~135
    thumb_ratio = min(1.0, scroll_y / 140.0)
    thumb_y = sb_y + int(max_thumb_travel * thumb_ratio)
    draw.rounded_rectangle((sb_x, thumb_y, sb_x + 4, thumb_y + thumb_h), radius=2, fill=(86, 95, 105))

    # --- 4. Right Panel: Real-Time Hand Vision & Diagnostics ---
    vx, vy, vw, vh = 480, 68, 300, 340
    draw.rounded_rectangle((vx, vy, vx + vw, vy + vh), radius=8, fill=(22, 27, 34), outline=(48, 54, 61))

    # Vision Camera Header
    draw.text((vx + 16, vy + 12), "LIVE VISION (WEBCAM)", fill=(240, 246, 252), font=font_h1)
    draw.ellipse((vx + vw - 28, vy + 16, vx + vw - 16, vy + 28), fill=(239, 68, 68) if not is_peace else (34, 197, 94))

    # Camera viewfinder viewport box
    cam_bx, cam_by, cam_bw, cam_bh = vx + 15, vy + 38, vw - 30, 185
    draw.rounded_rectangle((cam_bx, cam_by, cam_bx + cam_bw, cam_by + cam_bh), radius=6, fill=(13, 17, 23), outline=(48, 54, 61))

    # Subtle grid lines in viewport
    for gx in range(cam_bx + 30, cam_bx + cam_bw, 40):
        draw.line((gx, cam_by, gx, cam_by + cam_bh), fill=(20, 26, 35), width=1)
    for gy in range(cam_by + 30, cam_by + cam_bh, 40):
        draw.line((cam_bx, gy, cam_bx + cam_bw, gy), fill=(20, 26, 35), width=1)

    # Draw the dynamic hand skeleton inside viewport
    draw_hand_skeleton(draw, cam_bx + cam_bw // 2, cam_by + cam_bh // 2, peace_ratio, is_peace)

    # Corner viewfinder brackets
    c_len = 12
    draw.line((cam_bx + 6, cam_by + 6, cam_bx + 6 + c_len, cam_by + 6), fill=(56, 189, 248), width=2)
    draw.line((cam_bx + 6, cam_by + 6, cam_bx + 6, cam_by + 6 + c_len), fill=(56, 189, 248), width=2)
    draw.line((cam_bx + cam_bw - 6, cam_by + 6, cam_bx + cam_bw - 6 - c_len, cam_by + 6), fill=(56, 189, 248), width=2)
    draw.line((cam_bx + cam_bw - 6, cam_by + 6, cam_bx + cam_bw - 6, cam_by + 6 + c_len), fill=(56, 189, 248), width=2)
    draw.line((cam_bx + 6, cam_by + cam_bh - 6, cam_bx + 6 + c_len, cam_by + cam_bh - 6), fill=(56, 189, 248), width=2)
    draw.line((cam_bx + 6, cam_by + cam_bh - 6, cam_bx + 6, cam_by + cam_bh - 6 - c_len), fill=(56, 189, 248), width=2)
    draw.line((cam_bx + cam_bw - 6, cam_by + cam_bh - 6, cam_bx + cam_bw - 6 - c_len, cam_by + cam_bh - 6), fill=(56, 189, 248), width=2)
    draw.line((cam_bx + cam_bw - 6, cam_by + cam_bh - 6, cam_bx + cam_bw - 6, cam_by + cam_bh - 6 - c_len), fill=(56, 189, 248), width=2)

    # Diagnostic Status Badge Below Camera
    draw.rounded_rectangle((vx + 15, vy + 232, vx + vw - 15, vy + 270), radius=6, fill=(13, 17, 23), outline=status_color)
    draw.text((vx + 25, vy + 242), status_label, fill=status_color, font=font_badge)

    # Features check list
    draw.text((vx + 18, vy + 282), "✔ Fist-Proof (Closed palm ignored)", fill=(139, 148, 158), font=font_body)
    draw.text((vx + 18, vy + 300), "✔ Smooth reading pace (Ultra Slow)", fill=(139, 148, 158), font=font_body)
    draw.text((vx + 18, vy + 318), "✔ Windows Tray (Zero visual clutter)", fill=(139, 148, 158), font=font_body)

    # --- 5. Bottom Advertising Banner / Caption ---
    banner_y = 420
    draw.rounded_rectangle((20, banner_y, WIDTH - 20, banner_y + 48), radius=8, fill=(22, 27, 34), outline=(48, 54, 61))

    # Pulsing dot
    dot_color = caption_color
    draw.ellipse((38, banner_y + 19, 50, banner_y + 31), fill=dot_color)

    # Main dynamic caption text
    draw.text((62, banner_y + 14), caption_text, fill=caption_color, font=font_caption)

    # Downward scrolling indicators on browser if active
    if is_peace:
        pulse_offset = (frame_num % 10) * 2
        draw.polygon([(bx + bw - 35, by + 180 + pulse_offset),
                      (bx + bw - 20, by + 180 + pulse_offset),
                      (bx + bw - 27, by + 192 + pulse_offset)], fill=(34, 197, 94))

    return img

def main():
    print(f"[*] Rendering {TOTAL_FRAMES} frames for promo video & animated GIF...")
    frames = []

    # Setup MP4 video writer
    mp4_path = os.path.join("assets", "demo.mp4")
    gif_path = os.path.join("assets", "demo.gif")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(mp4_path, fourcc, FPS, (WIDTH, HEIGHT))

    for i in range(TOTAL_FRAMES):
        frame_img = render_frame(i)
        frames.append(frame_img)

        # Convert to BGR for OpenCV VideoWriter
        bgr_frame = cv2.cvtColor(np.array(frame_img), cv2.COLOR_RGB2BGR)
        video_writer.write(bgr_frame)

        if (i + 1) % 40 == 0 or i == TOTAL_FRAMES - 1:
            print(f"    Rendered {i + 1}/{TOTAL_FRAMES} frames ({(i + 1)/TOTAL_FRAMES*100:.1f}%)")

    video_writer.release()
    print(f"[+] MP4 Video generated successfully: {mp4_path} ({os.path.getsize(mp4_path)} bytes)")

    # Save animated GIF (sample every 2nd frame to keep file size lightweight ~3-4 MB for fast GitHub loading)
    print("[*] Generating optimized animated GIF for GitHub README...")
    # Step by 2 gives 10 fps, smooth and lightweight for web
    gif_frames = frames[::2]
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=100,  # 100ms = 10 fps
        loop=0,
        optimize=True
    )
    print(f"[+] Animated GIF generated successfully: {gif_path} ({os.path.getsize(gif_path)} bytes)")

if __name__ == "__main__":
    main()
