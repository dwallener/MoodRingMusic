import numpy as np
import io
import os
from scipy.io import wavfile
from scipy.signal import resample

class AudioRenderer:
    def __init__(self, sample_rate=44100, sample_folder="samples"):
        self.sample_rate = sample_rate
        self.sample_folder = sample_folder
        self.loaded_samples = {}
        self._load_samples()

    def _load_samples(self):
        for filename in os.listdir(self.sample_folder):
            if filename.endswith(".wav"):
                note_name = filename.replace(".wav", "")
                path = os.path.join(self.sample_folder, filename)
                sr, data = wavfile.read(path)
                self.loaded_samples[note_name] = (sr, data.astype(np.float32) / 32768.0)

    def _pitch_shift_sample(self, base_sample, base_freq, target_freq, duration_sec):
        sr, data = base_sample
        factor = target_freq / base_freq
        target_length = int(len(data) / factor)
        resampled = resample(data, target_length)
        if len(resampled) < int(self.sample_rate * duration_sec):
            resampled = np.pad(resampled, (0, int(self.sample_rate * duration_sec) - len(resampled)))
        return resampled[:int(self.sample_rate * duration_sec)]

    def generate_song_audio(self, bpm, key_root="C", scale_type="major", melody_notes=None, duration_sec=30):
        beats_per_sec = bpm / 60
        t = np.linspace(0, duration_sec, int(self.sample_rate * duration_sec), endpoint=False)
        modulation = (np.sin(2 * np.pi * beats_per_sec * t) > 0).astype(float)

        # Basic rhythm layers (kick/snare)
        kick = 0.3 * np.sin(2 * np.pi * 60 * t) * modulation
        snare = 0.2 * np.random.randn(len(t)) * (1 - modulation)

        # Pad (simple sustained chord using sine waves)
        pad_freqs = [261.63, 329.63, 392.00]  # C major chord
        pad = sum(0.1 * np.sin(2 * np.pi * f * t) for f in pad_freqs)

        # Melody using loaded samples
        melody = np.zeros_like(t)
        beats_total = int(duration_sec * beats_per_sec)
        if melody_notes:
            full_melody = (melody_notes * ((beats_total // len(melody_notes)) + 1))[:beats_total]
            note_duration_sec = 60 / bpm

            for i, midi_note in enumerate(full_melody):
                freq = 440.0 * (2 ** ((midi_note - 69) / 12))
                start = int(i * note_duration_sec * self.sample_rate)
                end = int((i + 1) * note_duration_sec * self.sample_rate)
                if end > len(t):
                    break

                # Use base sample closest to target note (C4, E4, G4 as examples)
                base_sample = None
                base_freq = None
                for base_note in ["C4", "E4", "G4"]:
                    if base_note in self.loaded_samples:
                        base_freq = self._note_to_freq(base_note)
                        base_sample = self.loaded_samples[base_note]
                        break

                if base_sample:
                    tone = self._pitch_shift_sample(base_sample, base_freq, freq, (end - start) / self.sample_rate)
                    melody[start:end] = tone[:end - start]

            melody *= 0.8  # Adjust melody volume

        # Final mix and normalization
        combined = kick + snare + pad + melody
        combined = combined / np.max(np.abs(combined))
        audio_wave = (combined * 32767).astype(np.int16)
        return audio_wave

    def export_wav(self, audio_data):
        buffer = io.BytesIO()
        wavfile.write(buffer, self.sample_rate, audio_data)
        buffer.seek(0)
        return buffer

    def _note_to_freq(self, note_name):
        note_freq_map = {"C4": 261.63, "E4": 329.63, "G4": 392.00}
        return note_freq_map.get(note_name, 261.63)