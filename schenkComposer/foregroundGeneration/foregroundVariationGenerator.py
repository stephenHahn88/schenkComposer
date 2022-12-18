from schenkComposer.foregroundGeneration.foregroundMelodyGenerator import generateForegroundMelodyUntilValid
from schenkComposer.middlegroundGeneration.harmonyMarkovChain import HarmonyMarkovChain

from schenkComposer.music21Wrappers.note import Note
from schenkComposer.music21Wrappers.romanNumeral import RomanNumeral

from schenkComposer.utility import contoursFromNotes


def basicIdeaHarmonyVariation(
        notes: list[Note],
        harmonies: list[RomanNumeral],
        harmonyMarkovChain: HarmonyMarkovChain
):
    newHarmonies = harmonyMarkovChain.forwardsFromHarmony(harmonies[-1].romanNumeral, len(harmonies))
    print(newHarmonies)


if __name__ == "__main__":
    notes, harmonies = generateForegroundMelodyUntilValid()
    print([h.romanNumeral for h in harmonies])
    basicIdeaHarmonyVariation(notes, harmonies, HarmonyMarkovChain())



