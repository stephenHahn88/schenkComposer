from music21.roman import RomanNumeral as RN
from fractions import Fraction


class RomanNumeral(RN):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.key.tonicPitchNameWithCase}: {self.romanNumeral}: {self.quarterLength}"

    def __repr__(self):
        return f"{self.key.tonicPitchNameWithCase}: {self.romanNumeral}: {self.quarterLength}"
