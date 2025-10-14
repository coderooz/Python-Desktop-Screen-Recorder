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