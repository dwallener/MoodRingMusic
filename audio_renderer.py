import numpy as np
import io
from scipy.io import wavfile

class AudioRenderer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def square_wave_arpeggio(self, base_frequency, bpm, duration_sec=4):
        t = np.linspace(0, duration_sec, int(self.sample_rate * duration_sec), endpoint=False)
        beats_per_sec = bpm / 60
        modulation = (np.sin(2 * np.pi * beats_per_sec * t) > 0).astype(float)

        arpeggio_notes = [base_frequency, base_frequency * 1.25, base_frequency * 1.5]
        note_length_samples = int(len(t) / len(arpeggio_notes))

        audio_wave = np.zeros_like(t)
        for i, freq in enumerate(arpeggio_notes):
            start = i * note_length_samples
            end = min(start + note_length_samples, len(t))
            audio_wave[start:end] = 0.5 * np.sign(np.sin(2 * np.pi * freq * t[start:end]))

        audio_wave *= modulation
        return (audio_wave * 32767).astype(np.int16)

    def export_wav(self, audio_data):
        buffer = io.BytesIO()
        wavfile.write(buffer, self.sample_rate, audio_data)
        buffer.seek(0)
        return buffer


