from music21.key import Key

from schenkComposer.foregroundGeneration.foregroundMelodyGenerator import generateForegroundMelodyUntilValid
from schenkComposer.middlegroundGeneration.chordMember import ChordMember
from schenkComposer.utility import noteListHarmonyListToMidi, noteListToMidi, noteListHarmonyListToScore
from schenkComposer.middlegroundGeneration.harmonyMarkovChain import HarmonyMarkovChain
from schenkComposer.music21Wrappers.note import Note
from time import strftime, gmtime

from schenkComposer.utility import makeRoman
from copy import deepcopy
from random import choices

from music21.scale import WholeToneScale, MinorScale


def harmonyAblation(preset: tuple):
    harmonyMarkovChain = HarmonyMarkovChain(
        transitionMatrix=preset[0],
        labels=preset[1]
    )
    endHarmonies = choices(harmonyMarkovChain.labels, k=2)

    scale = MinorScale("f#")
    key = Key("f#")
    roughness = 0
    a, h1 = generateForegroundMelodyUntilValid(phraseEnd=False, endHarmony="iv", numMeasures=4, harmonyMarkovChain=harmonyMarkovChain, scale=scale, key=key, maxRoughness=roughness)
    c, h3 = generateForegroundMelodyUntilValid(phraseEnd=True, endHarmony="i", numMeasures=4, endOn=ChordMember.ROOT, harmonyMarkovChain=harmonyMarkovChain, scale=scale, key=key, maxRoughness=roughness)
    notes = a + c
    harmonies = h1 + h3
    print(notes)
    print(harmonies)
    noteListHarmonyListToScore(
        notes,
        harmonies,
        f"../score/minor{strftime('%H_%M_%S', gmtime())}.xml"
    )


def middlegroundMelodyAblation():
    a, h1 = generateForegroundMelodyUntilValid(phraseEnd=False, endHarmony="V", numMeasures=4, middlegroundHarmonicRhythm="ablation")
    c, h3 = generateForegroundMelodyUntilValid(phraseEnd=True, endHarmony="I", numMeasures=4, endOn=ChordMember.ROOT, middlegroundHarmonicRhythm="ablation")
    notes = a + c
    harmonies = h1 + h3
    print(notes)
    print(harmonies)
    noteListHarmonyListToMidi(
        notes,
        harmonies,
        f"middlegroundRhythm/{strftime('%H_%M_%S', gmtime())}.mid"
    )


def smoothnessAblation():
    a, h1 = generateForegroundMelodyUntilValid(phraseEnd=False, endHarmony="V", numMeasures=4, maxRoughness=99, p=0.1)
    c, h3 = generateForegroundMelodyUntilValid(phraseEnd=True, endHarmony="I", numMeasures=4, endOn=ChordMember.ROOT, maxRoughness=99, p=0.1)
    notes = a + c
    harmonies = h1 + h3
    print(notes)
    print(harmonies)
    noteListHarmonyListToMidi(
        notes,
        harmonies,
        f"smoothness/{strftime('%H_%M_%S', gmtime())}.mid"
    )


if __name__ == "__main__":
    from schenkComposer.middlegroundGeneration.presetTransitionMatrices import CLASSICAL_MINOR_TRANSITION_MATRIX

    harmonyAblation(CLASSICAL_MINOR_TRANSITION_MATRIX)
    # middlegroundMelodyAblation()
    # smoothnessAblation()