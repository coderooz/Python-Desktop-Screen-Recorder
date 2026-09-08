# Project Reference Index (PRI)

**Project:** Python Desktop Screen Recorder
**Repository:** [coderooz/Python-Desktop-Screen-Recorder](https://github.com/coderooz/Python-Desktop-Screen-Recorder)
**Last Updated:** 2026-09-08
**Status:** Active — Archived (no active development)

---

## Purpose

This PRI provides a verified structural reference of the project's current state. It describes **where things are and what they do** — not why decisions were made (that lives in MCP memory).

---

## Directory Structure

```
Screen-Recorder/
├── main.py                          # Application entry point & GUI
├── recorder.py                      # Screen capture engine
├── editor.py                        # Video editor dialog
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation (renamed from READMD.md)
├── CHANGELOG.md                     # Version history
├── LICENSE                          # MIT License
├── AGENTS.md                        # Project governance & agent instructions
├── REPORT_INDEX.md                  # Generated reports index
├── .gitignore                       # Git ignore rules
├── .opencode/
│   └── reference/
│       └── PROJECT_REFERENCE_INDEX.md   # This file
├── .workspace/                      # Development artifacts (gitignored)
│   ├── reports/
│   ├── ai/
│   ├── sessions/
│   ├── temp/
│   └── planning/
├── docs/                            # Permanent documentation
│   └── DEVELOPER_NOTES.md
├── .github/                         # GitHub configuration (if present)
└── recordings/                      # Output directory (auto-created, gitignored)
```

---

## Source Files

### `main.py` — Application Entry Point

- **Purpose:** PySide6 GUI application — start/stop recording, preview, edit/export
- **Key Class:** `RecorderWindow(QtWidgets.QMainWindow)`
- **Dependencies:** `recorder.py`, `editor.py`, PySide6
- **Entry Point:** `if __name__ == '__main__': app = QtWidgets.QApplication(sys.argv)`
- **Output Directory:** `recordings/` (created at startup)

### `recorder.py` — Screen Capture Engine

- **Purpose:** Screen recording with optional audio capture
- **Key Class:** `ScreenRecorder`
- **Constructor Parameters:**
  - `output_path: str` — Final container path (.mkv)
  - `region: tuple` — Optional (x, y, w, h) for region capture
  - `fps: int` — Frames per second (default: 15)
  - `capture_audio: bool` — Enable audio capture (default: True)
  - `logger: callable` — Logging function
- **Methods:** `start()`, `stop()`, `_capture_video()`, `_capture_audio()`, `_finalize()`
- **Dependencies:** mss, cv2, sounddevice, soundfile, numpy, subprocess (ffmpeg)
- **Output:** Writes to temporary .avi (video) and .wav (audio), then muxes to .mkv via ffmpeg

### `editor.py` — Video Editor Dialog

- **Purpose:** Simple trimming and cropping editor
- **Key Class:** `VideoEditor(QtWidgets.QDialog)`
- **Constructor Parameters:**
  - `video_path: str` — Path to video file
  - `logger: callable` — Logging function
- **Features:** Start/end time trimming, pixel-wise cropping, external player preview
- **Dependencies:** PySide6, moviepy
- **Output:** Creates `{filename}_edited.{ext}` in same directory

---

## Dependencies (`requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| PySide6 | >=6.5.0 | Qt6 GUI framework |
| mss | >=7.0.0 | Cross-platform screen capture |
| numpy | >=1.24 | Array operations for frame processing |
| opencv-python-headless | >=4.7 | Video writing (AVI) and image processing |
| sounddevice | >=0.4.8 | Audio capture (WASAPI loopback) |
| soundfile | >=0.12.1 | WAV file writing |
| moviepy | >=1.0.3 | Video editing (trim/crop) |
| tqdm | >=4.65 | Progress bars (unused in current code) |
| ffmpeg-python | >=0.2.0 | FFmpeg wrapper (unused directly — subprocess used instead) |

**External Requirements:**
- `ffmpeg` binary must be installed and on PATH

---

## Configuration Files

| File | Purpose | Committed |
|------|---------|-----------|
| `.gitignore` | Git ignore rules | Yes |
| `.mcp-runtime.json` | MCP runtime state | Yes (root exception) |
| `docs-repo.project-mcp.json` | MCP project config | Yes (root exception) |
| `.vscode/` | VS Code settings | No (gitignored) |

---

## GitHub Repository

- **Remote:** `origin` → `https://github.com/coderooz/Python-Desktop-Screen-Recorder.git`
- **Branch:** `main` (only branch)
- **Commits:** 1 (Initial Commit)
- **Status:** Up to date with `origin/main`

---

## Output Files

- **Recordings Directory:** `recordings/` (auto-created at runtime)
- **File Pattern:** `recording_{timestamp}.mkv`
- **Edited Files:** `{original}_edited.{ext}` (created in same directory as original)

---

## Notes

- The README filename was originally `READMD.md` (typo) — renamed to `README.md` on 2026-09-08
- `tqdm` and `ffmpeg-python` are listed in requirements but not used in current code
- No automated test suite exists
- The application targets Windows (WASAPI loopback) but has basic cross-platform fallbacks
