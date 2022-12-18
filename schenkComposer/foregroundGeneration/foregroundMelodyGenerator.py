import string

from schenkComposer.middlegroundGeneration.chordMember import ChordMember
from schenkComposer.music21Wrappers.note import Note
from schenkComposer.contour.contour import Contour
from schenkComposer.music21Wrappers.romanNumeral import RomanNumeral
from schenkComposer.exceptions import InvalidSampleException
from schenkComposer.utility import findNearestNoteOfHarmonyAndRoughness, makeRomansWithKey
from schenkComposer.utility import findNearestNHTNote
from schenkComposer.utility import checkCorrectContour
from schenkComposer.middlegroundGeneration.middlegroundMelodyGenerator import smoothBackwardMiddlegroundMelodyGenerator
from schenkComposer.middlegroundGeneration.harmonyMarkovChain import HarmonyMarkovChain
from schenkComposer.middlegroundGeneration.harmonicRhythmGenerator import generateHarmonicRhythm
from schenkComposer.contour.contourPCFG import ContourPCFG
from schenkComposer.utility import makeRoman
from schenkComposer.middlegroundGeneration.middlegroundMelodyGenerator import generateMiddlegroundMelodyForSection
from schenkComposer.foregroundGeneration.foregroundRhythmGenerator import generateForegroundRhythm
from schenkComposer.config import PRODUCTIONS_JSON_PATH
from schenkComposer.utility import contourBetween, makeRomans
from schenkComposer.foregroundGeneration.stockRhythms import meters

from music21.meter import TimeSignature
from music21.key import Key
from music21.scale import ConcreteScale, MajorScale

from copy import deepcopy

from multipledispatch import dispatch
import numpy.random as nr
from random import choices


def generateNotesForOneHarmony(
        startNote: Note,
        endNote: Note,
        harmony: RomanNumeral,
        contours: list[Contour],
        scale: ConcreteScale = MajorScale("C"),
        maxRoughness: int = 1,
        distribution: str = "geometric",
        p: float = 0.6,
        includeNHT: bool = True
) -> list[Note]:
    notes = [startNote]
    for contour in contours[:-1]:
        # handle harmonic tones
        if contour.toNHT and includeNHT:
            nht = findNearestNHTNote(
                fromNote=notes[-1],
                harmony=harmony,
                contour=contour,
                scale=scale
            )
            notes.append(nht)
        # handle NHTs
        else:
            roughness = sampleRoughness(maxRoughness, distribution, p)
            leftNote = notes[-1]
            nextNote = findNearestNoteOfHarmonyAndRoughness(leftNote, harmony, contour, roughness)
            notes.append(nextNote)

    notes.append(endNote)
    if not checkCorrectContour(notes[-2], notes[-1], contours[-1]):
        raise InvalidSampleException

    return notes


def sampleRoughness(maxRoughness: int = 1, distribution: str = "geometric", p: float = 0.6) -> int:
    if distribution == "geometric":
        return min(nr.geometric(p, 1)[0] - 1, maxRoughness)
    elif distribution == "uniform":
        return choices(range(maxRoughness + 1), k=1)[0]
    else:
        raise NotImplementedError


def generateNotesForOneHarmonyUntilValid(
        fromNote: Note,
        toNote: Note,
        harmony: RomanNumeral,
        contours: list[Contour],
        scale: ConcreteScale = MajorScale("C"),
        maxRoughness: int = 1,
        distribution: str = "geometric",
        p: float = 0.6,
        includeNHT: bool = True
):
    tries = 0
    while True:
        tries += 1
        if tries > 100:
            raise InvalidSampleException
        try:
            notes = generateNotesForOneHarmony(
                fromNote,
                toNote,
                harmony,
                contours,
                maxRoughness=maxRoughness,
                scale=scale,
                distribution=distribution,
                p=p,
                includeNHT=includeNHT
            )
            break
        except InvalidSampleException:
            pass
    return notes


def generateForegroundMelody(
        timeSignature: TimeSignature = TimeSignature("4/4"),
        endHarmony: str = "I",
        numMeasures: int = 4,
        phraseEnd: bool = True,
        harmonyMarkovChain: HarmonyMarkovChain = HarmonyMarkovChain(),
        key: Key = Key("C"),
        endOn: ChordMember = None,
        scale: ConcreteScale = MajorScale("C"),
        maxRoughness: int = 1,
        distribution: str = "geometric",
        p: float = 0.6,
        middlegroundHarmonicRhythm: list = None,
        possibleHarmonicRhythms: list = None,
        middlegroundHarmony: list = None,
        middlegroundMelody: list = None,
        stockRhythms: dict = meters,
        includeNHT: bool = True,
        foregroundRhythm: list[tuple] = None
):
    if middlegroundHarmonicRhythm is None:
        middlegroundHarmonicRhythm = generateHarmonicRhythm(timeSignature, numMeasures, phraseEnd=phraseEnd,
                                                            possibleHarmonicRhythms=possibleHarmonicRhythms)
    if middlegroundHarmony is None:
        middlegroundHarmony = harmonyMarkovChain.backwardsFromHarmony(endHarmony,
                                                                      length=len(middlegroundHarmonicRhythm))
        middlegroundHarmony = makeRomansWithKey(middlegroundHarmony, rnKey=key)
        for i, rhythm in enumerate(middlegroundHarmonicRhythm):
            middlegroundHarmony[i].quarterLength = rhythm
    if middlegroundMelody is None:
        middlegroundMelody = smoothBackwardMiddlegroundMelodyGenerator(
            middlegroundHarmony,
            endOn=endOn
        )

    if foregroundRhythm is None:
        foregroundRhythm = generateForegroundRhythm(middlegroundHarmonicRhythm, timeSignature,
                                                    stockRhythms=stockRhythms)

    answer = [middlegroundMelody[0]]
    for i in range(len(middlegroundMelody) - 1):
        contour = contourBetween(middlegroundMelody[i], middlegroundMelody[i + 1])
        contour.setNumBetween(len(foregroundRhythm[i]))
        if len(foregroundRhythm[i]) > 1:
            pcfg = ContourPCFG(PRODUCTIONS_JSON_PATH, f"{contour.contourType.ascii()}{contour.numBetween}")
            contours = pcfg.generate(1)[0]
            # pcfg.printGenerated(contours)
            notes = generateNotesForOneHarmonyUntilValid(
                middlegroundMelody[i],
                middlegroundMelody[i + 1],
                middlegroundHarmony[i],
                contours,
                scale=scale,
                maxRoughness=maxRoughness,
                distribution=distribution,
                p=p,
                includeNHT=includeNHT
            )
            answer += notes[1:]
        else:
            answer += [middlegroundMelody[i + 1]]

    foregroundRhythm = [ql for group in foregroundRhythm for ql in group]
    for i, rhythm in enumerate(foregroundRhythm):
        answer[i].quarterLength = rhythm

    return answer, middlegroundHarmony


def generateForegroundMelodyUntilValid(
        timeSignature: TimeSignature = TimeSignature("4/4"),
        endHarmony: str = "I",
        numMeasures: int = 4,
        phraseEnd: bool = True,
        harmonyMarkovChain: HarmonyMarkovChain = HarmonyMarkovChain(),
        key: Key = Key("C"),
        endOn: ChordMember = None,
        scale: ConcreteScale = MajorScale("C"),
        maxRoughness: int = 1,
        distribution: str = "geometric",
        p: float = 0.6,
        middlegroundHarmonicRhythm: list = None,
        possibleHarmonicRhythms: list = None,
        middlegroundHarmony: list = None,
        middlegroundMelody: list = None,
        stockRhythms: dict = meters,
        includeNHT: bool = True,
        foregroundRhythm: list[tuple] = None
):
    for i in range(500):
        try:
            # print("---------------------------------------------")
            notes, harmony = generateForegroundMelody(
                timeSignature,
                endHarmony,
                numMeasures,
                phraseEnd,
                harmonyMarkovChain,
                key,
                endOn,
                scale=scale,
                maxRoughness=maxRoughness,
                distribution=distribution,
                p=p,
                middlegroundHarmonicRhythm=middlegroundHarmonicRhythm,
                possibleHarmonicRhythms=possibleHarmonicRhythms,
                middlegroundHarmony=middlegroundHarmony,
                middlegroundMelody=middlegroundMelody,
                stockRhythms=stockRhythms,
                includeNHT=includeNHT,
                foregroundRhythm=foregroundRhythm
            )
            # print("SUCCESS")
            return notes, harmony
        except:
            if i % 50 == 0:
                print("still trying")
    print("Too many tries :(")


if __name__ == "__main__":
    from schenkComposer.utility import noteListHarmonyListToMidi

    notes, harmony = generateForegroundMelodyUntilValid(

    )
    print(notes)
    print(harmony)
    noteListHarmonyListToMidi(notes, harmony)
