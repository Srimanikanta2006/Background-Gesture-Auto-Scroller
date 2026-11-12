# Background Hand Gesture Auto-Scroller

A lightweight, 100% free background tool for Windows that scrolls your screen down automatically when you show a **2-finger peace sign** to your webcam.

Perfect for hands-free reading of long answers on **ChatGPT**, research articles, tutorials, and ebooks.

---

## Why You'll Love This

- **Completely Invisible**: Runs silently in your Windows System Tray (near the clock). No camera preview popups, no command prompt windows.
- **Ultra-Slow Reading Speed**: Smooth line-by-line gliding so you can comfortably read without text flying past.
- **High-Precision Hand Recognition**:
  - Showing **2 fingers (✌ peace sign)** $\rightarrow$ Scrolls down.
  - Making a **fist / closing palm** $\rightarrow$ Instantly stops scrolling.
  - Showing **open palm (5 fingers)** or **1 finger** $\rightarrow$ Does not scroll.
- **100% Private & Offline**: All processing happens locally on your computer with Google MediaPipe. No images are saved or sent over the internet.
- **Zero Cost**: Built completely with free Python libraries.

---

## Quick Start (1 Minute Setup)

### Step 1: Install
1. Clone or download this repository.
2. Double-click **`setup.bat`**.
   *(This automatically creates a virtual environment and installs the required packages).*

### Step 2: Run in Background
- Double-click **`start_silent.vbs`**.
- That's it! It is now running silently in the background.

---

## How to Use

1. Open your browser with ChatGPT or any long article.
2. Put your hand in front of your webcam and raise **2 fingers (Index + Middle)**.
3. The page will smoothly scroll down while you read!
4. Lower your hand or close your fingers into a fist to stop immediately.

---

## Hand Gestures Cheat Sheet

| Gesture | What You Do | Result |
|---|---|---|
| **✌ Peace Sign** | Index & Middle fingers raised upward | **Smooth Auto-Scroll** |
| **✊ Fist / Closed Palm** | Fingers folded into palm | **Stop (Idle)** |
| **🖐 Open Hand** | All 5 fingers extended | **Stop (Idle)** |
| **☝ Pointing** | Only 1 finger raised | **Stop (Idle)** |

---

## System Tray Controls

Look at the bottom-right of your Windows taskbar (near the clock). You will find a small circular tray icon. Right-click it anytime to:

- **Pause / Resume**: Temporarily turn off gesture tracking without closing the app.
- **Scroll Speed**: Choose between *Ultra Slow (Reading)*, *Slow*, *Normal*, or *Fast*.
- **Show Camera Test (Preview)**: Opens a small camera window so you can check your lighting and see your hand skeleton live. Press `q` to close it.
- **Exit Gesture Scroller**: Cleanly stops the tool and frees your camera.

---

## Stopping the Tool

You can stop the scroller in two ways:
1. Right-click the system tray icon and click **Exit Gesture Scroller**, or
2. Double-click **`stop.bat`** to safely terminate the background process.

---

## Testing Your Camera (Optional)

Want to see how accurately your hand is being tracked?
Double-click **`test_camera.py`** to launch a visual tester window with live feedback banners. Press `q` when done.
