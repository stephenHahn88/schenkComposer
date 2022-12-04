from music21.note import Note as N
from fractions import Fraction


class Note(N):
    def __init__(self, *args, middleground=False, nht=False, onStrong=False, quarterLength=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.middleground = middleground
        self.nonHarmonicTone = nht
        self.onStrong = onStrong
        self.quarterLength = quarterLength

    def __repr__(self):
        return f"{self.nameWithOctave}: " \
               f"{self.quarterLength}" \
               f"{' MIDDLEGROUND' if self.middleground else ''}" \
               f"{' NHT' if self.nonHarmonicTone else ''}" \
               f"{' ON_STRONG' if self.onStrong else ''}"

