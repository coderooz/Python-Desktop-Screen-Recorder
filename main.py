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