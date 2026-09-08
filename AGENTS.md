# AGENTS.md — Project Governance & Agent Instructions

**Project:** Python Desktop Screen Recorder
**Repository:** [coderooz/Python-Desktop-Screen-Recorder](https://github.com/coderooz/Python-Desktop-Screen-Recorder)
**Author:** Ranit Saha (Coderooz)
**License:** MIT

---

## Project Overview

A deployment-ready desktop screen recorder written in Python with a PySide6 GUI. Features include screen recording (full screen or region), system audio capture via WASAPI loopback, video preview/editing with trimming and cropping, and FFmpeg-based muxing.

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| GUI Framework | PySide6 (Qt6) |
| Screen Capture | mss |
| Video Processing | OpenCV (cv2), moviepy, ffmpeg |
| Audio Capture | sounddevice, soundfile |
| Packaging | PyInstaller (optional) |

---

## Project Structure

```
Screen-Recorder/
├── main.py              # PySide6 GUI application entry point
├── recorder.py          # ScreenRecorder class (video + audio capture)
├── editor.py            # VideoEditor class (trim/crop dialog)
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── CHANGELOG.md         # Version history
├── LICENSE              # MIT License
├── AGENTS.md            # This file — project governance
├── REPORT_INDEX.md      # Generated reports index
├── .gitignore           # Git ignore rules
├── .opencode/
│   └── reference/
│       └── PROJECT_REFERENCE_INDEX.md   # PRI — structural reference
├── .workspace/          # Development artifacts (not committed)
├── docs/                # Permanent documentation
│   └── DEVELOPER_NOTES.md
├── .github/             # GitHub configuration (if present)
└── recordings/          # Output directory (auto-created, gitignored)
```

---

## Mandatory Rules for Agents

### Pre-Task

1. **Read this file** (AGENTS.md) before starting any task
2. **Read the PRI** at `.opencode/reference/PROJECT_REFERENCE_INDEX.md`
3. **Check CHANGELOG.md** for current version and recent changes
4. **Review `requirements.txt`** before modifying dependencies

### Code Standards

- Use `snake_case` for functions and variables
- Use `PascalCase` for classes
- Keep functions focused and under 50 lines where possible
- Add docstrings to public methods
- Use type hints where practical
- Follow PEP 8 conventions

### File Placement (Governance)

- **Root-level files:** Only `AGENTS.md`, `README.md`, `CHANGELOG.md`, `LICENSE`, `REPORT_INDEX.md`, `.gitignore`, `requirements.txt`, `*.project-mcp.json`, `.mcp-runtime.json`
- **Documentation:** Place in `docs/`
- **Development artifacts:** Place in `.workspace/` (not committed)
- **Reports:** Place in `.workspace/reports/` with naming `{CATEGORY}_{DESCRIPTOR}_{YYYYMMDD}.md`

### Testing

- No formal test framework currently configured
- Manual testing: run `python main.py` and verify recording/editing functions
- Ensure `ffmpeg` is installed and on PATH before testing

### Commit Conventions

- Follow conventional commits: `type(scope): message`
- Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `style`, `perf`
- Scope examples: `recorder`, `editor`, `gui`, `build`

---

## Known Issues & Limitations

1. **Windows-only WASAPI:** System audio capture relies on WASAPI loopback (Windows). Linux/macOS require alternative loopback devices.
2. **FFmpeg dependency:** Requires `ffmpeg` binary installed separately and on PATH.
3. **No test suite:** No automated tests exist yet.
4. **moviepy performance:** Video editing via moviepy can be slow for large files.

---

## Development Commands

```bash
# Setup virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

# Package with PyInstaller
pip install pyinstaller
pyinstaller --noconfirm --onefile main.py
```

---

## External Dependencies

- **ffmpeg:** Must be installed separately. Download from [ffmpeg.org](https://ffmpeg.org/) and add to PATH.
- **WASAPI loopback:** Windows-only. Used for system audio capture.

---

## Version

Current: **1.0.0** (Initial Release)

---

## Contact

- **Author:** Ranit Saha
- **Brand:** Coderooz
- **GitHub:** [coderooz](https://github.com/coderooz)
- **Email:** contact@coderooz.in
- **Website:** coderooz.in
