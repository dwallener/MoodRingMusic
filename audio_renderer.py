import numpy as np
import io
from scipy.io import wavfile

class AudioRenderer:
    NOTE_MAP = {
        "C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23,
        "G": 392.00, "A": 440.00, "B": 493.88
    }
    SCALES = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10]
    }

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def sine_wave(self, frequency, duration_sec):
        t = np.linspace(0, duration_sec, int(self.sample_rate * duration_sec), endpoint=False)
        return 0.3 * np.sin(2 * np.pi * frequency * t)

    def square_wave(self, frequency, duration_sec):
        t = np.linspace(0, duration_sec, int(self.sample_rate * duration_sec), endpoint=False)
        return 0.3 * np.sign(np.sin(2 * np.pi * frequency * t))

    def noise_burst(self, duration_sec):
        return 0.2 * np.random.randn(int(self.sample_rate * duration_sec))

    def get_scale_frequencies(self, key_root, scale_type):
        root_freq = self.NOTE_MAP.get(key_root, 261.63)
        intervals = self.SCALES.get(scale_type, self.SCALES["major"])
        return [root_freq * (2 ** (i / 12)) for i in intervals]

    def generate_song_audio(self, bpm, key_root="C", scale_type="major", duration_sec=4):
        beats_per_sec = bpm / 60
        t = np.linspace(0, duration_sec, int(self.sample_rate * duration_sec), endpoint=False)
        modulation = (np.sin(2 * np.pi * beats_per_sec * t) > 0).astype(float)

        scale_freqs = self.get_scale_frequencies(key_root, scale_type)

        # Rhythm section (Kick + Snare)
        kick = self.sine_wave(60, duration_sec) * modulation
        snare = self.noise_burst(duration_sec) * (1 - modulation)
        pad = sum(self.sine_wave(f, duration_sec) for f in scale_freqs[:3]) * 0.2

        # Melody with BPM-tied timing
        melody = np.zeros_like(t)
        beats_total = duration_sec * beats_per_sec
        melody_notes = scale_freqs[:4]  # Pick first 4 notes from scale

        # One melody note per beat
        for i in range(int(beats_total)):
            freq = melody_notes[i % len(melody_notes)]
            start = int(i * (self.sample_rate / beats_per_sec))
            end = int((i + 1) * (self.sample_rate / beats_per_sec))
            if end > len(t):  # Prevent overflow
                break
            tone = self.square_wave(freq * 2, (end - start) / self.sample_rate)
            melody[start:end] = tone[:end - start]

        melody *= 0.8  # Boost melody volume slightly

        # Mix tracks
        combined = kick + snare + pad + melody
        combined = combined / np.max(np.abs(combined))
        audio_wave = (combined * 32767).astype(np.int16)
        return audio_wave

    def export_wav(self, audio_data):
        buffer = io.BytesIO()
        wavfile.write(buffer, self.sample_rate, audio_data)
        buffer.seek(0)
        return buffer