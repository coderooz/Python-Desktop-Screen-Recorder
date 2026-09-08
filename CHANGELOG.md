# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2025-10-14

### Added

- **Screen Recording:** Full screen or region-based capture using `mss`
- **Audio Capture:** System audio via WASAPI loopback (Windows) using `sounddevice`
- **Video Muxing:** Automatic muxing of audio and video into MKV via `ffmpeg`
- **GUI Interface:** PySide6-based desktop application with start/stop controls
- **Video Editor:** Simple trimming and cropping dialog using `moviepy`
- **Region Selection:** Configurable X, Y, Width, Height for partial screen recording
- **Output Management:** Timestamped recording files in `recordings/` directory
- **External Preview:** Open recordings in default system player

### Technical Details

- Video capture: `mss` → OpenCV `VideoWriter` (XVID/AVI) → `ffmpeg` mux to MKV
- Audio capture: `sounddevice` InputStream → WAV → `ffmpeg` mux with AAC
- Finalization: `ffmpeg -i video.avi -i audio.wav -c:v copy -c:aaac output.mkv`
- Temporary files (`.video.avi`, `.audio.wav`) cleaned up after muxing

---

## [Unreleased]

### Governance & Documentation (2026-09-08)

- Renamed `READMD.md` to `README.md` (fixed typo)
- Added `AGENTS.md` — project governance and agent instructions
- Added `CHANGELOG.md` — version history
- Added `LICENSE` — MIT License
- Added `.opencode/reference/PROJECT_REFERENCE_INDEX.md` — PRI
- Added `REPORT_INDEX.md` — generated reports index
- Added `docs/DEVELOPER_NOTES.md` — developer onboarding documentation
- Updated `.gitignore` with comprehensive entries
- Created `.workspace/` directory structure (gitignored)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2025-10-14 | Initial release — screen recorder with audio, GUI, and editor |
| Unreleased | 2026-09-08 | Governance compliance, documentation, repository cleanup |
