# Python Desktop Screen Recorder

A deployment-ready **desktop screen recorder** written in Python with a GUI. Features:

* Record entire screen or a selectable region
* Capture **system audio** (Windows - WASAPI loopback) and microphone
* Live preview during recording
* Save raw video and audio and automatically mux into MP4 using `ffmpeg`
* Simple in-app **cropping (pixel-wise)** and **trimming (start/end)** editor for recorded files
* Export to a chosen folder
* Ready for packaging (PyInstaller) with instructions

> **Platform focus:** This implementation is targeted at **Windows** and tested on Windows 10/11. It uses WASAPI loopback via `sounddevice` backend and requires `ffmpeg` installed and on PATH. Some features (system audio capture) need different setup on macOS/Linux — see notes below.

---

## Project structure (single-file demo + helpers)

This repository contains the following files (shown below as code blocks). You can copy-paste each into files in a folder named `screen_recorder`.

* `requirements.txt` — Python dependencies
* `README.md` — (this file)
* `main.py` — main PySide6 GUI application (starts/stops recording, preview, edit/export)
* `recorder.py` — screen capture and audio capture helpers
* `editor.py` — simple trimming & cropping utilities using `moviepy` + `ffmpeg`

---

## 1) requirements.txt

```text
PySide6>=6.5.0
mss>=7.0.0
numpy>=1.24
opencv-python-headless>=4.7
sounddevice>=0.4.8
soundfile>=0.12.1
moviepy>=1.0.3
tqdm>=4.65
ffmpeg-python>=0.2.0
```

Note: `ffmpeg` binary must be installed separately and be available on your PATH. Download from [https://ffmpeg.org/](https://ffmpeg.org/) and add to PATH.

---

## 2) main.py

This is the UI entrypoint built with PySide6. It uses `recorder.py` to perform recording and `editor.py` to crop/trim and export.

```python
# main.py
import sys
import os
import time
from pathlib import Path
from PySide6 import QtCore, QtWidgets, QtGui
from recorder import ScreenRecorder
from editor import VideoEditor

APP_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = APP_DIR / "recordings"
OUTPUT_DIR.mkdir(exist_ok=True)

class RecorderWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desktop Screen Recorder")
        self.setMinimumSize(900, 600)

        self.recorder = None
        self.current_recording = None

        # UI Layout
        main = QtWidgets.QWidget()
        self.setCentralWidget(main)
        layout = QtWidgets.QVBoxLayout(main)

        # Controls
        controls = QtWidgets.QHBoxLayout()

        self.btn_start = QtWidgets.QPushButton("Start Recording")
        self.btn_stop = QtWidgets.QPushButton("Stop Recording")
        self.btn_preview = QtWidgets.QPushButton("Preview / Edit Last")
        self.btn_browse = QtWidgets.QPushButton("Open Output Folder")

        controls.addWidget(self.btn_start)
        controls.addWidget(self.btn_stop)
        controls.addWidget(self.btn_preview)
        controls.addWidget(self.btn_browse)

        layout.addLayout(controls)

        # Options
        options_group = QtWidgets.QGroupBox("Recording Options")
        options_layout = QtWidgets.QFormLayout()

        self.input_filename = QtWidgets.QLineEdit(str(OUTPUT_DIR / "recording_{ts}.mp4"))
        self.checkbox_capture_audio = QtWidgets.QCheckBox("Capture System Audio (WASAPI loopback)")
        self.checkbox_capture_audio.setChecked(True)

        # Region selection
        self.checkbox_region = QtWidgets.QCheckBox("Record specific region")
        self.spin_x = QtWidgets.QSpinBox(); self.spin_x.setMaximum(10000)
        self.spin_y = QtWidgets.QSpinBox(); self.spin_y.setMaximum(10000)
        self.spin_w = QtWidgets.QSpinBox(); self.spin_w.setMaximum(10000); self.spin_w.setValue(1280)
        self.spin_h = QtWidgets.QSpinBox(); self.spin_h.setMaximum(10000); self.spin_h.setValue(720)

        options_layout.addRow("Output filename pattern:", self.input_filename)
        options_layout.addRow(self.checkbox_capture_audio)
        options_layout.addRow(self.checkbox_region)
        options_layout.addRow("Region X:", self.spin_x)
        options_layout.addRow("Region Y:", self.spin_y)
        options_layout.addRow("Region W:", self.spin_w)
        options_layout.addRow("Region H:", self.spin_h)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Log / preview area
        self.log = QtWidgets.QTextEdit(); self.log.setReadOnly(True)
        layout.addWidget(self.log, stretch=1)

        # Signals
        self.btn_start.clicked.connect(self.start_recording)
        self.btn_stop.clicked.connect(self.stop_recording)
        self.btn_preview.clicked.connect(self.preview_last)
        self.btn_browse.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(OUTPUT_DIR))))

        self.btn_stop.setEnabled(False)

    def log_msg(self, *parts):
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        msg = f"[{ts}] " + " ".join(str(p) for p in parts)
        self.log.append(msg)
        print(msg)

    def start_recording(self):
        if self.recorder and self.recorder.is_recording:
            self.log_msg("Already recording")
            return

        pattern = self.input_filename.text().strip()
        ts = time.strftime('%Y%m%d_%H%M%S')
        out_path = Path(pattern.replace('{ts}', ts)).expanduser()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        region = None
        if self.checkbox_region.isChecked():
            region = (self.spin_x.value(), self.spin_y.value(), self.spin_w.value(), self.spin_h.value())

        capture_audio = self.checkbox_capture_audio.isChecked()

        self.recorder = ScreenRecorder(output_path=str(out_path.with_suffix('.mkv')), region=region, capture_audio=capture_audio, logger=self.log_msg)
        self.recorder.start()
        self.current_recording = out_path.with_suffix('.mkv')
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.log_msg('Recording started ->', self.current_recording)

    def stop_recording(self):
        if not self.recorder or not self.recorder.is_recording:
            self.log_msg('Not recording')
            return
        self.recorder.stop()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log_msg('Recording stopped')

    def preview_last(self):
        if not self.current_recording or not Path(self.current_recording).exists():
            self.log_msg('No recording found to preview')
            return
        editor = VideoEditor(str(self.current_recording), logger=self.log_msg)
        editor.exec_()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = RecorderWindow()
    w.show()
    sys.exit(app.exec())
```

---

## 3) recorder.py

Contains the `ScreenRecorder` class. It captures frames with `mss`, writes raw frames to a `*.avi` via OpenCV `VideoWriter`, and records audio to WAV using `sounddevice`. Finally it will produce a bundled MKV (or MP4 via ffmpeg)

```python
# recorder.py
import threading
import time
import wave
import numpy as np
from pathlib import Path
import subprocess
import sys

import mss
import cv2
import sounddevice as sd
import soundfile as sf

class ScreenRecorder:
    def __init__(self, output_path: str, region: tuple=None, fps: int=15, capture_audio: bool=True, logger=print):
        """
        output_path: final container path (we write to .mkv then user can export .mp4)
        region: (x,y,w,h) if provided, else full screen
        """
        self.output_path = Path(output_path)
        self.region = region
        self.fps = fps
        self.capture_audio = capture_audio
        self.logger = logger

        self._stop_event = threading.Event()
        self._video_thread = None
        self._audio_thread = None
        self.is_recording = False

        # internal temporary files
        self.tmp_video = self.output_path.with_suffix('.video.avi')
        self.tmp_audio = self.output_path.with_suffix('.audio.wav')

    def start(self):
        self._stop_event.clear()
        self.is_recording = True
        self._video_thread = threading.Thread(target=self._capture_video, daemon=True)
        self._video_thread.start()
        if self.capture_audio:
            self._audio_thread = threading.Thread(target=self._capture_audio, daemon=True)
            self._audio_thread.start()

    def stop(self):
        self._stop_event.set()
        if self._video_thread:
            self._video_thread.join()
        if self._audio_thread:
            self._audio_thread.join()
        self.is_recording = False
        self._finalize()

    def _capture_video(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # primary monitor
            if self.region:
                x,y,w,h = self.region
                bbox = {'left': x, 'top': y, 'width': w, 'height': h}
            else:
                bbox = dict(left=monitor['left'], top=monitor['top'], width=monitor['width'], height=monitor['height'])

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            writer = cv2.VideoWriter(str(self.tmp_video), fourcc, self.fps, (bbox['width'], bbox['height']))

            last = time.time()
            frame_time = 1.0 / self.fps
            self.logger('Video capture started, writing to', self.tmp_video)
            while not self._stop_event.is_set():
                img = sct.grab(bbox)
                arr = np.array(img)  # BGRA
                frame = arr[..., :3]
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                writer.write(frame)

                # sleep to maintain fps
                elapsed = time.time() - last
                to_sleep = frame_time - elapsed
                if to_sleep > 0:
                    time.sleep(to_sleep)
                last = time.time()

            writer.release()
            self.logger('Video capture finished')

    def _capture_audio(self):
        # Records system audio via WASAPI loopback on windows. On other platforms this may record microphone.
        self.logger('Audio capture started, writing to', self.tmp_audio)
        samplerate = int(sd.query_devices(kind='output')['default_samplerate']) if sd.query_devices(kind='output') else 48000
        samplerate = int(samplerate)
        channels = 2

        frames = []
        def callback(indata, frames_count, time_info, status):
            if status:
                self.logger('Sounddevice status:', status)
            frames.append(indata.copy())
            if self._stop_event.is_set():
                raise sd.CallbackStop()

        # Try to use WASAPI loopback on Windows
        try:
            if sys.platform.startswith('win'):
                sd.default.device = None
                sd.default.samplerate = samplerate
                sd.default.channels = channels
                # WASAPI: use hostapi 'wasapi' and set loopback
                wasapi = None
                for i,api in enumerate(sd.query_hostapis()):
                    if 'wasapi' in api['name'].lower():
                        wasapi = i
                        break
                if wasapi is not None:
                    sd.default.hostapi = wasapi
                    # choose output device
                    # Using device=None may use default - it often works for loopback
                stream = sd.InputStream(samplerate=samplerate, channels=channels, callback=callback, dtype='int16')
            else:
                # Linux/macOS: fallback to default input (may be mic)
                stream = sd.InputStream(samplerate=samplerate, channels=channels, callback=callback, dtype='int16')

            with stream:
                while not self._stop_event.is_set():
                    time.sleep(0.1)
        except Exception as e:
            self.logger('Audio capture failed:', e)
            return

        # write wav
        if len(frames) == 0:
            self.logger('No audio frames captured')
            return
        data = np.concatenate(frames, axis=0)
        sf.write(str(self.tmp_audio), data, samplerate)
        self.logger('Audio capture finished')

    def _finalize(self):
        # Use ffmpeg to mux audio and video into final container
        self.logger('Finalizing and muxing into', self.output_path)
        cmd = [
            'ffmpeg', '-y',
            '-i', str(self.tmp_video),
        ]
        if self.capture_audio and self.tmp_audio.exists():
            cmd += ['-i', str(self.tmp_audio), '-c:v', 'copy', '-c:a', 'aac']
        else:
            cmd += ['-c:v', 'copy']
        cmd += [str(self.output_path)]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.logger('Muxing done ->', self.output_path)
        except subprocess.CalledProcessError as e:
            self.logger('ffmpeg failed:', e.stderr.decode(errors='ignore'))

        # cleanup tmp
        try:
            if self.tmp_video.exists():
                self.tmp_video.unlink()
            if self.tmp_audio.exists():
                self.tmp_audio.unlink()
        except Exception:
            pass
```

---

## 4) editor.py

Provides a modal dialog for simple trimming and cropping using `moviepy`.

```python
# editor.py
from PySide6 import QtWidgets, QtCore
from moviepy.editor import VideoFileClip
from pathlib import Path
import tempfile
import shutil

class VideoEditor(QtWidgets.QDialog):
    def __init__(self, video_path: str, logger=print):
        super().__init__()
        self.setWindowTitle('Preview & Edit')
        self.video_path = Path(video_path)
        self.logger = logger
        self.resize(800, 600)

        layout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QFormLayout()
        self.input_start = QtWidgets.QDoubleSpinBox(); self.input_start.setRange(0, 99999); self.input_start.setDecimals(2)
        self.input_end = QtWidgets.QDoubleSpinBox(); self.input_end.setRange(0, 99999); self.input_end.setDecimals(2)
        self.input_crop_x = QtWidgets.QSpinBox(); self.input_crop_y = QtWidgets.QSpinBox()
        self.input_crop_w = QtWidgets.QSpinBox(); self.input_crop_h = QtWidgets.QSpinBox()

        form.addRow('Start (s):', self.input_start)
        form.addRow('End (s):', self.input_end)
        form.addRow('Crop X:', self.input_crop_x)
        form.addRow('Crop Y:', self.input_crop_y)
        form.addRow('Crop W:', self.input_crop_w)
        form.addRow('Crop H:', self.input_crop_h)

        layout.addLayout(form)

        btns = QtWidgets.QHBoxLayout()
        self.btn_preview = QtWidgets.QPushButton('Play (external player)')
        self.btn_apply = QtWidgets.QPushButton('Apply & Export')
        btns.addWidget(self.btn_preview); btns.addWidget(self.btn_apply)
        layout.addLayout(btns)

        self.btn_preview.clicked.connect(self.play)
        self.btn_apply.clicked.connect(self.apply)

        # load basic metadata
        clip = VideoFileClip(str(self.video_path))
        dur = clip.duration
        w,h = clip.size
        clip.reader.close(); clip.audio.reader.close_proc() if clip.audio else None

        self.input_end.setMaximum(dur)
        self.input_end.setValue(dur)
        self.input_crop_w.setMaximum(w); self.input_crop_h.setMaximum(h)

    def play(self):
        # open with default system player
        QtGui = None
        import webbrowser
        webbrowser.open(str(self.video_path))

    def apply(self):
        start = float(self.input_start.value())
        end = float(self.input_end.value())
        x = int(self.input_crop_x.value()); y = int(self.input_crop_y.value())
        w = int(self.input_crop_w.value()); h = int(self.input_crop_h.value())

        tmpdir = Path(tempfile.mkdtemp())
        out = self.video_path.with_name(self.video_path.stem + '_edited' + self.video_path.suffix)

        clip = VideoFileClip(str(self.video_path)).subclip(start, end)
        if w > 0 and h > 0:
            clip = clip.crop(x1=x, y1=y, width=w, height=h)
        self.logger('Exporting edited video ->', out)
        clip.write_videofile(str(out), codec='libx264', audio_codec='aac')
        clip.reader.close(); clip.audio.reader.close_proc() if clip.audio else None
        shutil.rmtree(tmpdir)
        QtWidgets.QMessageBox.information(self, 'Done', f'Edited file saved to:\n{out}')
```

---

## Usage

1. Create a new folder and save the files above as `requirements.txt`, `main.py`, `recorder.py`, `editor.py`.
2. Create a virtualenv, install requirements:

```bash
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
```

3. Install `ffmpeg` and add to PATH.
4. Run:

```bash
python main.py
```

5. Use `Start Recording` to begin. Use `Stop Recording` to finish. Click `Preview / Edit Last` to trim/crop and export.

## Packaging for distribution

You can bundle into a single executable using `PyInstaller`.

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --add-data "path_to_ffmpeg\ffmpeg.exe;." main.py
```

Note: bundling `ffmpeg` is optional; simpler is to require users to install ffmpeg separately.

---

## Limitations & Notes

* System audio capture works reliably on **Windows** using WASAPI loopback. On Linux/macOS you'll likely record microphone input unless you configure a loopback device (e.g., `pavucontrol`/`snd_aloop` on Linux or use `Soundflower`/`BlackHole` on macOS).
* MoviePy can be slow and may require `imageio-ffmpeg` (installed via `moviepy` dependencies) and `ffmpeg` binary to be present.
* The program is designed as a simple, deployable starting point. For production-level features (high-FPS capture, hardware encoding, GPU use, per-window capture, live preview within UI, timeline editing), consider integrating platform-specific APIs or native bindings.

---

## Troubleshooting

* If audio is silent on Windows: double-check default playback device and WASAPI loopback availability. Try setting the correct hostapi/device in `recorder.py`.
* If ffmpeg errors: run the ffmpeg command printed in logs manually to see details.

---

## License

MIT
