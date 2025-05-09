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

    def _add_variation(self, motif):
        varied = motif[:]
        idx = random.randint(0, len(varied) - 1)
        change = random.choice([-1, 1])
        varied[idx] = max(21, min(108, varied[idx] + change))
        return varied

    def _snap_to_scale(self, motif):
        return [min(self.scale_notes, key=lambda s: abs(s - note)) for note in motif]

    def generate_melody(self, length=16):
        melody = []
        motif_length = 4
        transformations = ['invert', 'retrograde', 'transpose', 'original', 'variation']
        last_transform = None

        while len(melody) < length:
            if len(melody) % 8 == 0 or last_transform == 'original':
                motif = random.choices(self.scale_notes, k=motif_length)

            available_transforms = [t for t in transformations if t != last_transform]
            transform = random.choice(available_transforms)

            if transform == 'invert':
                new_motif = self._invert(motif)
            elif transform == 'retrograde':
                new_motif = self._retrograde(motif)
            elif transform == 'transpose':
                steps = random.choice([-2, -1, 1, 2])
                new_motif = self._transpose(motif, steps)
            elif transform == 'variation':
                new_motif = self._add_variation(motif)
            else:
                new_motif = motif

            # Snap notes back to the scale after transformation
            new_motif = self._snap_to_scale(new_motif)
            melody.extend(new_motif)
            last_transform = transform

        return melody[:length]