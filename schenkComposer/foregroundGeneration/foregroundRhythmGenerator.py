from schenkComposer.foregroundGeneration.stockRhythms import meters

from music21.meter import TimeSignature
from random import sample


def generateForegroundRhythm(
        middlegroundHarmonicRhythm: list[float],
        timeSignature: TimeSignature,
        stockRhythms: dict = meters
) -> list[tuple]:
    """
    Generates foreground rhythm using a set of stock rhythms
    :param middlegroundHarmonicRhythm: The middleground harmonic rhythm, which is broken into the foreground rhythm
    :param timeSignature: Music21 TimeSignature object
    :param stockRhythms: The dict of possible rhythms
    :return: Foreground rhythm in the form of [(2, 1), (1, 1, 1), ...] where each tuple adds up to a harmonic rhythm
    """
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



