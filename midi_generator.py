
import mido
import io

class MidiGenerator:
    def __init__(self, bpm=120):
        self.bpm = bpm
        self.ticks_per_beat = 480
        self.mid = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)

    def generate_song(self):
        kick_track = mido.MidiTrack()
        snare_track = mido.MidiTrack()
        pad_track = mido.MidiTrack()
        chord_track = mido.MidiTrack()
        melody_track = mido.MidiTrack()

        tempo = mido.bpm2tempo(self.bpm)
        for track in [kick_track, snare_track, pad_track, chord_track, melody_track]:
            track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        
        ticks = int(self.ticks_per_beat / 2)

        # Kick: beats 1, 2, 3, 4
        for i in range(4):
            kick_track.append(mido.Message('note_on', note=36, velocity=100, time=i * ticks))
            kick_track.append(mido.Message('note_off', note=36, velocity=0, time=ticks))

        # Snare: beats 2 & 4
        for i in [1, 3]:
            snare_track.append(mido.Message('note_on', note=38, velocity=100, time=i * ticks))
            snare_track.append(mido.Message('note_off', note=38, velocity=0, time=ticks))

        # Simple sustained pad chord (C major)
        for note in [60, 64, 67]:
            pad_track.append(mido.Message('note_on', note=note, velocity=50, time=0))
            pad_track.append(mido.Message('note_off', note=note, velocity=50, time=ticks * 8))

        # Chord stabs
        for i in range(4):
            for note in [60, 64, 67]:
                chord_track.append(mido.Message('note_on', note=note, velocity=80, time=i * ticks * 2))
                chord_track.append(mido.Message('note_off', note=note, velocity=80, time=ticks))

        # Melody: Simple arpeggio
        melody_notes = [72, 76, 79, 76]
        for i, note in enumerate(melody_notes):
            melody_track.append(mido.Message('note_on', note=note, velocity=90, time=i * ticks))
            melody_track.append(mido.Message('note_off', note=note, velocity=90, time=ticks))

        self.mid.tracks.extend([kick_track, snare_track, pad_track, chord_track, melody_track])

    def export(self):
        buffer = io.BytesIO()
        self.mid.save(file=buffer)
        buffer.seek(0)
        return buffer
