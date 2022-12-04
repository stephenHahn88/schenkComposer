from __future__ import annotations

from enum import Enum
from music21.note import Note
from music21.interval import Interval


class ContourType(Enum):
    UP = ("\u2197", "u")
    DOWN = ("\u2198", "d")
    STRAIGHT = ("\u2192", "s")

    def ascii(self):
        return self.value[1]

    def __str__(self):
        return self.value[0]

    def __repr__(self):
        return f"{self.name} - {self.value}"

    @staticmethod
    def between(fromNote: Note, toNote: Note) -> ContourType:
        """Finds the contourType between two notes"""
        interval = Interval(fromNote, toNote)
        if interval.semitones > 0:
            return ContourType.UP
        elif interval.semitones < 0:
            return ContourType.DOWN
        else:
            return ContourType.STRAIGHT


if __name__ == "__main__":
    u = ContourType.UP
    print(repr(u))

