import mido
import io
import random

from markov_melody import MarkovMelodyGenerator
from motif_melody import MotifMelodyGenerator


class MidiGenerator:
    KEY_MAPPINGS = {
        ("Enhance", "High"): ("C", "major"),
        ("Enhance", "Low"): ("A", "major"),
        ("Neutral", None): ("G", "major"),
        ("Oppose", "High"): ("A", "minor"),
        ("Oppose", "Low"): ("E", "minor"),
    }

    NOTE_MAP = {"C": 60, "D": 62, "E": 64, "F": 65, "G": 67, "A": 69, "B": 71}
    SCALES = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10]}

    def __init__(self, bpm=120, alignment="Neutral", energy="Moderate"):
        self.bpm = bpm
        self.ticks_per_beat = 480
        self.mid = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        self.key_root, self.scale_type = self.select_key(alignment, energy)

    def select_key(self, alignment, energy):
        for (align, ener), (key, scale) in self.KEY_MAPPINGS.items():
            if alignment.startswith(align) and (ener is None or ener == energy):
                return key, scale
        return "C", "major"

    def get_scale_notes(self):
        root_note = self.NOTE_MAP[self.key_root]
        intervals = self.SCALES[self.scale_type]
        return [root_note + i for i in intervals]

    def generate_song(self):
        scale_notes = self.get_scale_notes()
        track = mido.MidiTrack()
        self.mid.tracks.append(track)
        tempo = mido.bpm2tempo(self.bpm)
        track.append(mido.MetaMessage('set_tempo', tempo=tempo))

        ticks = int(self.ticks_per_beat / 2)

        # Choose the melody generator you want to use:
        melody_generator = MarkovMelodyGenerator(scale_notes)  # Or MotifMelodyGenerator(scale_notes)
        melody_notes = melody_generator.generate_melody(length=8)

        # Add the generated melody notes to the MIDI track:
        for note in melody_notes:
            track.append(mido.Message('note_on', note=note, velocity=64, time=0))
            track.append(mido.Message('note_off', note=note, velocity=64, time=ticks))

    def export(self):
        buffer = io.BytesIO()
        self.mid.save(file=buffer)
        buffer.seek(0)
        return buffer