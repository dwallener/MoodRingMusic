import io
import mido

class MidiGenerator:
    def __init__(self, bpm=120):
        self.bpm = bpm
        self.ticks_per_beat = 480
        self.mid = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        self.track = mido.MidiTrack()
        self.mid.tracks.append(self.track)
        self.set_tempo()

    def set_tempo(self):
        tempo = mido.bpm2tempo(self.bpm)
        self.track.append(mido.MetaMessage('set_tempo', tempo=tempo))

    def add_note_sequence(self, notes, note_duration_beats=0.5):
        ticks = int(self.ticks_per_beat * note_duration_beats)
        for note in notes:
            self.track.append(mido.Message('note_on', note=note, velocity=64, time=0))
            self.track.append(mido.Message('note_off', note=note, velocity=64, time=ticks))

    def export(self):
        buffer = io.BytesIO()
        self.mid.save(file=buffer)  # Use 'file=' to write to a buffer
        buffer.seek(0)
        return buffer