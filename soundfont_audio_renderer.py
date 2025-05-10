# SoundFont version for local generation
import io
import os
import random
import numpy as np
import fluidsynth
from scipy.io.wavfile import write

class SoundFontAudioRenderer:
    def __init__(self, soundfont_path="soundfonts/FluidR3_GM.sf2", sample_rate=44100, bank=0, program=0):
        self.sample_rate = sample_rate
        self.fs = fluidsynth.Synth(samplerate=sample_rate)
        self.fs.start(driver="file")  # Prevent trying to use system audio drivers
        self.sfid = self.fs.sfload(soundfont_path)
        self.bank = bank
        self.program = program
        self.set_instrument(bank, program)
        self.fs.cc(0, 7, 127)  # Max out volume for channel 0

    def set_instrument(self, bank, program):
        self.bank = bank
        self.program = program
        self.fs.program_select(0, self.sfid, bank, program)

    def generate_song_audio(self, bpm, key_root="C", scale_type="major", melody_notes=None, duration_sec=30, energy="Moderate"):
        beats_per_sec = bpm / 60
        note_duration_sec = 60 / bpm
        total_notes = int(duration_sec * beats_per_sec)
        melody_notes = (melody_notes * ((total_notes // len(melody_notes)) + 1))[:total_notes]

        audio = []

        for midi_note in melody_notes:
            velocity = random.randint(80, 127)
            adjusted_duration_sec = note_duration_sec * random.uniform(0.8, 1.2)

            self.fs.program_select(0, self.sfid, self.bank, self.program)
            self.fs.noteon(0, midi_note, velocity)

            sample_count = int(self.sample_rate * adjusted_duration_sec)
            samples = self.fs.get_samples(sample_count)

            self.fs.noteoff(0, midi_note)
            audio.extend(samples)

        audio_np = (np.array(audio) * 32767).astype(np.int16)
        return audio_np

    def export_wav(self, audio_data):
        buffer = io.BytesIO()
        write(buffer, self.sample_rate, audio_data)
        buffer.seek(0)
        return buffer

    def __del__(self):
        self.fs.delete()