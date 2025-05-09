import random

class MotifMelodyGenerator:
    def __init__(self, scale_notes):
        self.scale_notes = scale_notes

    def _invert(self, motif):
        center = motif[0]
        return [center - (note - center) for note in motif]

    def _retrograde(self, motif):
        return motif[::-1]

    def _transpose(self, motif, steps):
        return [note + steps for note in motif]

    def generate_melody(self, length=8):
        # Step 1: Create a base motif (random 4-note phrase)
        motif = random.choices(self.scale_notes, k=4)
        melody = motif.copy()

        # Step 2: Apply transformations to fill the requested length
        while len(melody) < length:
            transform = random.choice(['invert', 'retrograde', 'transpose', 'original'])
            if transform == 'invert':
                new_motif = self._invert(motif)
            elif transform == 'retrograde':
                new_motif = self._retrograde(motif)
            elif transform == 'transpose':
                steps = random.choice([-2, -1, 1, 2])
                new_motif = self._transpose(motif, steps)
            else:
                new_motif = motif

            # Keep notes within valid scale range (MIDI range safe)
            new_motif = [max(21, min(108, n)) for n in new_motif]
            melody.extend(new_motif)

        return melody[:length]

