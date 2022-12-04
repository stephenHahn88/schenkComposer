from schenkComposer.music21Wrappers.note import Note
from schenkComposer.music21Wrappers.romanNumeral import RomanNumeral
from schenkComposer.form.cadence import Cadence

from music21.key import Key
from random import choices
import numpy as np

class HarmonyMarkovChain():
    def __init__(self,
                 transitionMatrix: np.array = None,
                 labels: list[str] = None,
                 key: Key = Key("C")
                 ):
        if transitionMatrix is None:
            self.transitions = np.array([
                [0, 0, 0, 0, 9, 0, 1], # I
                [1, 0, 0, 3, 0, 1, 0], # ii
                [1, 0, 0, 0, 0, 3, 0], # iii
                [1, 1, 1, 0, 0, 2, 0], # IV
                [1, 3, 0, 2, 0, 1, 0], # V
                [1, 0, 1, 0, 1, 0, 0], # vi
                [1, 1, 1, 1, 0, 0, 0]  # viio
            ], dtype=float)

            for i in range(self.transitions.shape[0]):
                self.transitions[i] = self.transitions[i] / sum(self.transitions[i])
        else:
            self.transitions = transitionMatrix

        if labels is None:
            self.labels = ["I", "ii", "iii", "IV", "V", "vi", "viio6"]
        else:
            self.labels = labels

        if self.transitions.shape[0] != self.transitions.shape[1]:
            raise ValueError(
                f"transition matrix must be square. "
                f"Got shape {self.transitions.shape} instead"
            )
        if self.transitions.shape[0] != len(self.labels):
            raise ValueError(
                f"transition matrix and labels do not match length. "
                f"Got {self.transitions.shape[0]} and {len(self.labels)} instead"
            )
        self.key = key

    def backwardsFromHarmony(self, harmony: str, length: int = 5) -> list[str]:
        progression = [harmony]
        progression = self._forwardPass(progression, length)
        return list(reversed(progression))

    def _forwardPass(self, progression, length) -> list[str]:
        for i in range(length-1):
            index = self.labels.index(progression[i])
            next = choices(self.labels, weights=self.transitions[index], k=1)[0]
            progression.append(next)
        return progression


if __name__ == "__main__":
    hpg = HarmonyMarkovChain()
    for _ in range(10):
        print(hpg.backwardsFromHarmony("ii"))










