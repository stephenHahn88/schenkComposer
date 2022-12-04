from music21.meter import TimeSignature
from random import choices


def getCommonHarmonicRhythmsForSingleMeasure(timeSignature: TimeSignature) -> tuple:
    beatsPerMeasure = timeSignature.beatCount
    if beatsPerMeasure == 2:
        return (2,), (1, 1)
    elif beatsPerMeasure == 3:
        return (3,), (2, 1)
    elif beatsPerMeasure == 4:
        return (4,), (2, 2), (3, 1)#, (1, 1, 1, 1)
    elif beatsPerMeasure == 5:
        return (5,), (3, 2), (2, 3), (4, 1)
    else:
        raise NotImplementedError


def generateHarmonicRhythm(timeSignature: TimeSignature, numMeasures: int, phraseEnd: bool = True, possibleHarmonicRhythms=None) -> list[float]:
    beatQuarterLength = timeSignature.beatDuration.quarterLength
    if possibleHarmonicRhythms is None:
        possibleHarmonicRhythms = getCommonHarmonicRhythmsForSingleMeasure(timeSignature)
    if phraseEnd:
        answer = [beats * beatQuarterLength for measure in choices(possibleHarmonicRhythms, k=numMeasures-1) for beats in measure]
        answer += [timeSignature.numerator * (1/timeSignature.denominator) * 4]
    else:
        return [beats * beatQuarterLength for measure in choices(possibleHarmonicRhythms, k=numMeasures) for beats in measure]
    return answer

if __name__ == "__main__":
    print(generateHarmonicRhythm(TimeSignature("12/8"), 4, False))


