import random

import numpy as np


CLASSICAL_TRANSITION_MATRIX = {
    "matrix": np.array([
        [0, 0, 0, 0, 9, 0, 1], # I
        [1, 0, 0, 3, 0, 1, 0], # ii
        [1, 0, 0, 0, 0, 3, 0], # iii
        [1, 1, 1, 0, 0, 2, 0], # IV
        [1, 3, 0, 2, 0, 1, 0], # V
        [1, 0, 1, 0, 1, 0, 0], # vi
        [1, 1, 1, 1, 0, 0, 0]  # viio
    ], dtype=float),
    "labels": ["I", "ii", "iii", "IV", "V", "vi", "viio6"]
}


CLASSICAL_MINOR_TRANSITION_MATRIX = {
    "matrix": np.array([
        [0, 0, 0, 0, 9, 0, 1], # I
        [1, 0, 0, 3, 0, 1, 0], # ii
        [1, 0, 0, 0, 0, 3, 0], # iii
        [1, 1, 1, 0, 0, 2, 0], # IV
        [1, 3, 0, 2, 0, 1, 0], # V
        [1, 0, 1, 0, 1, 0, 0], # vi
        [1, 1, 1, 1, 0, 0, 0]  # viio
    ], dtype=float),
    "labels": ["i", "iio6", "III", "iv", "V", "VI", "viio6"]
}


ROCK_TRANSITION_MATRIX = {
    "matrix": np.array([
        [2, 0, 0, 5, 5, 0, 0], #I
        [1, 2, 0, 1, 1, 2, 0], #ii
        [1, 0, 2, 0, 1, 1, 0], #iii
        [1, 4, 1, 2, 4, 1, 0], #IV
        [1, 2, 1, 4, 2, 2, 0], #V
        [1, 2, 1, 2, 4, 2, 0], #vi
        [1, 0, 0, 0, 0, 0, 1]
    ], dtype=float),
    "labels": ["I", "ii", "iii", "IV", "V", "vi", "viio6"]
}

CHINESE_TRANSITION_MATRIX = {
    "matrix": np.array([
        [0, 0, 5, 0],
        [2, 0, 0, 3],
        [1, 3, 0, 1],
        [1, 2, 4, 0]
    ], dtype=float),
    "labels": ["I", "iii[no5]", "V[no3]", "vi"]
}

GAGAKU_TRANSITION_MATRIX = {
    "matrix": np.array([
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1]
    ], dtype=float),
    "labels": [
        "I[no5][add2][add6][add7]", #bo
        "ii[no3][add4][add7][add#2]", #otsu
        "V[no3][add2][add4][add#6]", #gyo
        "vii[add4][add7]" # ichi
    ]
}

RANDOM_DIATONIC_TRANSITION_MATRIX = (
    np.random.random(size=(7, 7)),
    ["I", "ii", "iii", "IV", "V", "vi", "viio6"]
)


RANDOM_TRANSITION_MATRIX = (
    np.random.random(size=(7, 7)),
    random.choices([
        "I", "i", "ii", "II", "iii", "bIII", "iv", "IV",
        "V", "v", "vi", "VI", "bVI", "viio", "VII"
    ], k=7)
)

presetCollection = {
    "Classical_Major": CLASSICAL_TRANSITION_MATRIX,
    "Classical_Minor": CLASSICAL_MINOR_TRANSITION_MATRIX,
    "Rock": ROCK_TRANSITION_MATRIX,
    "Pentatonic": CHINESE_TRANSITION_MATRIX,
    "Random_Diatonic": RANDOM_DIATONIC_TRANSITION_MATRIX,
}

if __name__ == "__main__":
    m = ROCK_TRANSITION_MATRIX
    print("hi")
