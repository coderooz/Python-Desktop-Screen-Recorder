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