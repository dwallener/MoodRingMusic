import numpy as np
import io
import os
from scipy.io.wavfile import read, write
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
                sr, data = read(path)
                self.loaded_samples[note_name] = (sr, data.astype(np.float32) / 32768.0)

    def _pitch_shift_sample(self, base_sample, base_freq, target_freq, duration_sec):
        sr, data = base_sample
        factor = target_freq / base_freq
        target_length = int(len(data) / factor)
        resampled = resample(data, target_length)
        if len(resampled) < int(self.sample_rate * duration_sec):
            resampled = np.pad(resampled, (0, int(self.sample_rate * duration_sec) - len(resampled)))
        return resampled[:int(self.sample_rate * duration_sec)]

    def _note_to_freq(self, note_name):
        note_freq_map = {"C4": 261.63, "E4": 329.63, "G4": 392.00}
        return note_freq_map.get(note_name, 261.63)

    def _select_progression(self, energy):
        import random
        progressions = {
            "Lowest": [["C", "Am", "F", "G"]],
            "Low": [["C", "Dm", "G", "C"]],
            "Rising": [["C", "F", "G", "C"]],
            "Moderate": [["C", "Am", "F", "G"]],
            "High": [["C", "Em", "F", "G"]],
            "Decreasing": [["C", "F", "Dm", "G"]]
        }
        return random.choice(progressions.get(energy, [["C", "F", "G", "C"]]))

    def _chord_to_frequencies(self, chord):
        base_freqs = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, 
                      "G": 392.00, "A": 440.00, "B": 493.88}
        if chord.endswith("m"):
            root = chord[:-1]
            return [base_freqs[root], base_freqs[root] * 2 ** (3 / 12), base_freqs[root] * 2 ** (7 / 12)]
        else:
            return [base_freqs[chord], base_freqs[chord] * 2 ** (4 / 12), base_freqs[chord] * 2 ** (7 / 12)]

    def square_wave(self, frequency, duration_sec):
        t = np.linspace(0, duration_sec, int(self.sample_rate * duration_sec), endpoint=False)
        return 0.3 * np.sign(np.sin(2 * np.pi * frequency * t))

    def generate_song_audio(self, bpm, key_root="C", scale_type="major", melody_notes=None, duration_sec=30, energy="Moderate"):
        beats_per_sec = bpm / 60
        measure_beats = 4  # 4/4 Time
        measure_duration_sec = measure_beats / beats_per_sec

        # Snap to full measures for clean looping
        total_measures = max(1, int(duration_sec / measure_duration_sec))
        final_duration_sec = total_measures * measure_duration_sec

        # Recompute time array and related variables
        t = np.linspace(0, final_duration_sec, int(self.sample_rate * final_duration_sec), endpoint=False)
        beats_total = total_measures * measure_beats
        modulation = (np.sin(2 * np.pi * beats_per_sec * t) > 0).astype(float)

        kick = np.zeros_like(t)
        snare = np.zeros_like(t)
        beat_samples = int(self.sample_rate / beats_per_sec)

        for i in range(int(beats_total)):
            start = i * beat_samples
            end = start + beat_samples
            if end > len(t):
                end = len(t)
            sample_length = end - start

            if i % 4 == 0 and "kick" in self.loaded_samples:
                sr, kick_sample = self.loaded_samples["kick"]
                kick_data = kick_sample[:sample_length]
                if len(kick_data) < sample_length:
                    kick_data = np.pad(kick_data, (0, sample_length - len(kick_data)))
                kick[start:end] += kick_data

            if i % 4 == 2 and "snare" in self.loaded_samples:
                sr, snare_sample = self.loaded_samples["snare"]
                snare_data = snare_sample[:sample_length]
                if len(snare_data) < sample_length:
                    snare_data = np.pad(snare_data, (0, sample_length - len(snare_data)))
                snare[start:end] += snare_data

        # Chord Progressions (Pads)
        progression = self._select_progression(energy)
        chord_beats = len(progression)
        pad = np.zeros_like(t)

        for i in range(int(beats_total)):
            current_chord = progression[i % chord_beats]
            freqs = self._chord_to_frequencies(current_chord)
            start = i * beat_samples
            end = start + beat_samples
            if end > len(t):
                end = len(t)
            for f in freqs:
                pad[start:end] += 0.1 * np.sin(2 * np.pi * f * t[start:end])

        # Melody Section
        melody = np.zeros_like(t)
        if melody_notes:
            full_melody = (melody_notes * ((int(beats_total) // len(melody_notes)) + 1))[:int(beats_total)]
            note_duration_sec = 60 / bpm

            for i, midi_note in enumerate(full_melody):
                freq = 440.0 * (2 ** ((midi_note - 69) / 12))
                start = int(i * note_duration_sec * self.sample_rate)
                end = start + int(note_duration_sec * self.sample_rate)
                if end > len(t):
                    end = len(t)
                sample_length = end - start

                base_sample = self.loaded_samples.get("C4")
                if base_sample:
                    tone = self._pitch_shift_sample(base_sample, self._note_to_freq("C4"), freq, sample_length / self.sample_rate)
                    if len(tone) < sample_length:
                        tone = np.pad(tone, (0, sample_length - len(tone)))
                    melody[start:end] = tone[:sample_length]

            melody *= 0.8

        # Final Mix and Normalize
        combined = kick + snare + pad + melody
        combined = combined / np.max(np.abs(combined))
        audio_wave = (combined * 32767).astype(np.int16)
        return audio_wave

    def export_wav(self, audio_data):
        buffer = io.BytesIO()
        write(buffer, self.sample_rate, audio_data)
        buffer.seek(0)
        return buffer