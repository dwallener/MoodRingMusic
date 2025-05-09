import random

class MarkovMelodyGenerator:
    def __init__(self, scale_notes):
        self.scale_notes = scale_notes
        self.transition_prob = self._build_simple_transitions()

    def _build_simple_transitions(self):
        return {-1: 0.3, 0: 0.4, 1: 0.3}  # Move down, stay, move up

    def generate_melody(self, length=16, start_note=None):
        melody = []
        current_idx = self.scale_notes.index(start_note) if start_note in self.scale_notes else len(self.scale_notes) // 2

        for _ in range(length):
            melody.append(self.scale_notes[current_idx])
            move = random.choices(list(self.transition_prob.keys()), weights=self.transition_prob.values())[0]
            current_idx = max(0, min(len(self.scale_notes) - 1, current_idx + move))

        return melody