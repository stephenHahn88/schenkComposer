from schenkComposer.foregroundGeneration.stockRhythms import meters

from music21.meter import TimeSignature
from random import sample


def generateForegroundRhythm(
        middlegroundHarmonicRhythm: list[float],
        timeSignature: TimeSignature,
        stockRhythms=meters
) -> list[tuple]:
    meter = f"{timeSignature.numerator}/{timeSignature.denominator}"
    foregroundRhythm = []
    for rhythm in middlegroundHarmonicRhythm:
        options = stockRhythms[meter][rhythm]
        foregroundRhythm.append(sample(options, k=1)[0])
    return foregroundRhythm


if __name__ == "__main__":
    from schenkComposer.middlegroundGeneration.harmonicRhythmGenerator import generateHarmonicRhythm

    ts = TimeSignature("4/4")
    mghr = generateHarmonicRhythm(ts, 2)
    fgr = generateForegroundRhythm(mghr, ts)
    print(mghr, fgr)



