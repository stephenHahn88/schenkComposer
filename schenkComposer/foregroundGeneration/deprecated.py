from schenkComposer.form.cadence import Cadence
from schenkComposer.music21Wrappers.note import Note
from schenkComposer.contour.contour import Contour
from schenkComposer.contour.contourType import ContourType
from schenkComposer.music21Wrappers.romanNumeral import RomanNumeral
from schenkComposer.foregroundGeneration.nht import NHT
from schenkComposer.contour.contourPCFG import ContourPCFG
from schenkComposer.exceptions import InvalidSampleException
from schenkComposer.utility import findNearestNoteOfHarmonyAndRoughness
from schenkComposer.utility import findPossibleNHTs
from schenkComposer.utility import findClosestOfPitch
from schenkComposer.utility import getContourType
from schenkComposer.utility import findNearestNHTNote
from schenkComposer.utility import checkCorrectContour
from schenkComposer.foregroundGeneration.scale import scaleTones

from music21.interval import Interval
from music21.key import Key
from music21.meter import TimeSignature
from music21.scale import ConcreteScale, MajorScale

import numpy as np
import numpy.random as nr
from random import choices
from copy import deepcopy

from nltk.grammar import Nonterminal, Production, ProbabilisticProduction


def generateForegroundMelodyHarmonicNotes(
        startNote: Note,
        endNote: Note,
        contours: list[Contour],
        harmonies: list[RomanNumeral],
        maxRoughness: int
) -> list[Note]:
    # check input
    if maxRoughness < 0:
        raise ValueError(f"maxRoughness must be 0 or greater")
    if len(contours) != len(harmonies) - 1:
        raise ValueError(f"harmonies must contain one more item than contours "
                         f"because it includes harmonies for start and end notes. "
                         f"got contours len:{len(contours)}, harmonies len:{len(harmonies)} instead")
    # Determine the roughness for each note
    roughnesses = [min(r - 1, maxRoughness) for r in nr.geometric(0.5, len(contours) - 1)]

    newNotes = []
    currNote = startNote
    for i, (contour, harmony) in enumerate(zip(contours, harmonies[1:-1])):
        currNote = findNearestNoteOfHarmonyAndRoughness(currNote, harmony, contour, roughnesses[i])
        newNotes.append(currNote)

    # reject samples if the final contour is incorrect
    lastIntervalSemitones = Interval(currNote, endNote).semitones
    if (lastIntervalSemitones < 0 and contours[-1].contourType is not ContourType.DOWN) or \
            (lastIntervalSemitones > 0 and contours[-1].contourType is not ContourType.UP) or \
            (lastIntervalSemitones == 0 and contours[-1].contourType is not ContourType.STRAIGHT):
        raise InvalidSampleException()
    return newNotes


def generateNHT(
        startNote: Note,
        endNote: Note,
        nhtOnStrong: bool,
        chromatic: bool = False,
        scale: tuple[int] = (0, 2, 4, 5, 7, 9, 11),
        key: Key = Key("C")
) -> Note:
    """
    Generates an NHT between two given notes.
    :param startNote: the starting note
    :param endNote: the ending note
    :param nhtOnStrong: is the NHT on a strong beat
    :param chromatic: is the NHT chromatic vs. in the scale
    :param scale: tuple of chromatic scale degrees that belong to the scale
    :param key: local key
    :return: NHT as a Note
    """
    possibleNHTs = findPossibleNHTs(startNote, endNote, nhtOnStrong)
    distribution = [nhtType.value[1] for nhtType in possibleNHTs]
    distribution = [p / sum(distribution) for p in distribution]
    nhtType = choices(possibleNHTs, weights=distribution, k=1)[0]
    return _generateSpecificNHT(startNote, endNote, nhtType, chromatic, scale, key)


def _generateSpecificNHT(
        startNote: Note,
        endNote: Note,
        nhtType: NHT,
        chromatic: bool,
        scale: tuple[int],
        key: Key
) -> Note:
    """
    generate the exact note for the NHT
    """
    if nhtType in [NHT.SUSPENSION, NHT.RETARDATION]:
        return deepcopy(startNote)
    if nhtType is NHT.ANTICIPATION:
        return deepcopy(endNote)

    tonic = key.getTonic().pitchClass
    scaleLen = len(scale)

    startChromaticDegree = (startNote.pitch.pitchClass - tonic) % 12
    endChromaticDegree = (endNote.pitch.pitchClass - tonic) % 12

    if nhtType in [NHT.PASSING, NHT.UPPER_NEIGHBOR, NHT.UPPER_ESCAPE]:  # and interval >= 0:
        csd = scale[(scale.index(startChromaticDegree) + 1) % scaleLen]
    elif nhtType in [NHT.PASSING, NHT.LOWER_NEIGHBOR, NHT.LOWER_ESCAPE]:  # and interval <= 0:
        csd = scale[(scale.index(startChromaticDegree) - 1) % scaleLen]
    elif nhtType is NHT.UPPER_INCOMPLETE:
        csd = scale[(scale.index(endChromaticDegree) + 1) % scaleLen]
    elif nhtType is NHT.LOWER_INCOMPLETE:
        csd = scale[(scale.index(endChromaticDegree) - 1) % scaleLen]

    # TODO: Find a better way. Makes odd chromaticisms at times
    if chromatic:
        if (csd - 1) % 12 not in scale:
            csd = (csd - 1) % 12
        elif (csd + 1) % 12 not in scale:
            csd = (csd + 1) % 12

    if nhtType in [NHT.LOWER_ESCAPE, NHT.UPPER_ESCAPE]:
        baseNote = startNote
    else:
        baseNote = endNote

    try:
        newNote = key.getTonic().transpose(csd)
    except:
        raise InvalidSampleException()
    newNote = findClosestOfPitch(baseNote, newNote.name)
    return Note(newNote.nameWithOctave)
