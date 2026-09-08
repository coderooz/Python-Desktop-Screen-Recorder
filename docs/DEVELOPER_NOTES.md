# Developer Notes

**Project:** Python Desktop Screen Recorder
**Last Updated:** 2026-09-08
**For:** Future developers working on this project

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/coderooz/Python-Desktop-Screen-Recorder.git
cd Python-Desktop-Screen-Recorder

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install ffmpeg (required)
# Download from https://ffmpeg.org/ and add to PATH

# 5. Run the application
python main.py
```

---

## Architecture Overview

The application follows a simple 3-file architecture:

```
main.py  →  recorder.py  →  editor.py
   │              │              │
   │              │              └── Video trimming & cropping
   │              └── Screen + audio capture
   └── GUI & orchestration
```

### Data Flow

1. **Recording Phase:**
   - `main.py` creates `ScreenRecorder` instance
   - `recorder.py` spawns two daemon threads:
     - Video thread: `mss` → `cv2.VideoWriter` (XVID/AVI)
     - Audio thread: `sounddevice` → WAV buffer
   - On stop: `ffmpeg` muxes AVI + WAV → MKV

2. **Editing Phase:**
   - `main.py` opens `VideoEditor` dialog
   - `editor.py` loads video with `moviepy.VideoFileClip`
   - User sets trim/crop parameters
   - `moviepy` exports to `{name}_edited.{ext}`

---

## Key Implementation Details

### Video Capture (`recorder.py:54-84`)

```python
# Uses mss for screen capture, OpenCV for writing
# Frame timing is manual (sleep-based), not drift-corrected
# Output is AVI with XVID codec
```

- **Frame Rate:** Default 15 FPS (configurable)
- **Color Space:** BGRA from mss → BGR for OpenCV
- **Timing:** `time.sleep()` between frames — may drift under load

### Audio Capture (`recorder.py:86-135`)

```python
# Uses sounddevice with WASAPI loopback on Windows
# Falls back to default input (microphone) on other platforms
# Collects frames in memory, writes WAV at stop
```

- **Sample Rate:** Auto-detected from output device (default 48000)
- **Channels:** 2 (stereo)
- **Format:** int16 WAV

### FFmpeg Muxing (`recorder.py:137-163`)

```bash
# Command executed:
ffmpeg -y -i video.avi -i audio.wav -c:v copy -c:aac output.mkv
```

- `-c:v copy` — No re-encoding of video (fast)
- `-c:aac` — Re-encode audio to AAC
- Temporary files deleted after successful mux

### Video Editing (`editor.py`)

- Uses `moviepy.editor.VideoFileClip`
- Trimming: `clip.subclip(start, end)`
- Cropping: `clip.crop(x1, y1, width, height)`
- Export: `clip.write_videofile()` with libx264 + aac

---

## Common Development Tasks

### Adding a New Recording Feature

1. Modify `ScreenRecorder.__init__()` for new parameters
2. Update `main.py` GUI to expose new options
3. Update `_capture_video()` or `_capture_audio()` as needed
4. Test with different resolutions and frame rates

### Modifying the Editor

1. `editor.py` is self-contained — modify the `VideoEditor` class
2. moviepy docs: https://zulko.github.io/moviepy/
3. For complex editing, consider replacing moviepy with ffmpeg commands

### Changing Output Format

1. Modify `_finalize()` in `recorder.py`
2. Change ffmpeg arguments for different container/codec
3. Common alternatives:
   - MP4: `-c:v libx264 -c:a aac output.mp4`
   - WebM: `-c:v libvpx -c:a libvorbis output.webm`

---

## Platform-Specific Notes

### Windows

- WASAPI loopback works for system audio capture
- Requires Windows 10+ for WASAPI
- `sounddevice` must detect WASAPI host API

### Linux

- System audio capture requires loopback device:
  ```bash
  # Create loopback with pavucontrol or:
  sudo modprobe snd-aloop
  ```
- Use PulseAudio or PipeWire for audio routing

### macOS

- System audio capture requires third-party loopback:
  - [Soundflower](https://github.com/mattingalls/Soundflower)
  - [BlackHole](https://github.com/ExistentialAudio/BlackHole)
- Or use microphone input as fallback

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ffmpeg not found` | Install ffmpeg and add to PATH |
| No audio captured | Check WASAPI loopback; try different output device |
| Video is choppy | Lower FPS or increase `time.sleep()` interval |
| `cv2.VideoWriter` fails | Check codec support; try different fourcc |
| moviepy import error | Reinstall: `pip install moviepy --force-reinstall` |
| GUI doesn't appear | Ensure PySide6 installed: `pip install PySide6` |

---

## Performance Considerations

- **Frame Rate:** 15 FPS is default; 30 FPS increases file size ~2x
- **Resolution:** Full screen at 4K generates large AVI files
- **Audio Buffer:** All audio held in memory until stop — very long recordings may use significant RAM
- **FFmpeg Muxing:** Fast due to `-c:v copy` (no video re-encoding)

---

## Dependencies Deep Dive

| Package | Why Needed | Can Replace? |
|---------|-----------|--------------|
| `mss` | Fast cross-platform screen capture | `pyautogui`, `Pillow.ImageGrab` |
| `cv2` | Video writing and image processing | `imageio`, `av` |
| `sounddevice` | Audio capture via PortAudio | `pyaudio` |
| `soundfile` | WAV writing | `scipy.io.wavfile` |
| `moviepy` | Video editing | Direct ffmpeg calls |
| `PySide6` | Qt6 GUI | `tkinter`, `PyQt6` |
| `numpy` | Array operations | Included with most packages |

---

## Testing Strategy

No automated tests exist. Manual testing approach:

1. **Basic Recording:** Start → Record 5s → Stop → Verify MKV exists
2. **Region Recording:** Enable region → Set coordinates → Record → Verify dimensions
3. **Audio:** Record with audio enabled → Play MKV → Verify sound
4. **Editor:** Open editor → Set trim points → Apply → Verify output
5. **Edge Cases:** Very short recording, very long recording, no audio device

---

## Code Style Notes

- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_prefix` (e.g., `_capture_video`)
- Imports: stdlib → third-party → local (grouped)

---

## Git Workflow

- **Branch:** `main` (only branch)
- **Commits:** Conventional commits format
- **No CI/CD** configured
- **No automated testing** in pipeline

---

## Future Enhancements (Ideas)

- [ ] Live preview during recording
- [ ] Hardware-accelerated encoding (NVENC, VAAPI)
- [ ] Per-window recording
- [ ] Keyboard shortcuts
- [ ] Recording timer/counter
- [ ] Output format selection (MKV/MP4/WebM)
- [ ] FPS configuration in GUI
- [ ] Audio device selection
- [ ] Automated tests
- [ ] Cross-platform audio loopback setup guide

---

*This document is maintained for future developers. Update it when making significant changes.*
