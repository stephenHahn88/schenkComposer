from schenkComposer.music21Wrappers.romanNumeral import RomanNumeral
from schenkComposer.music21Wrappers.note import Note
from schenkComposer.middlegroundGeneration.chordMember import ChordMember
from schenkComposer.utility import findClosestOfPitch, findClosestOfNotes
from schenkComposer.middlegroundGeneration.harmonicRhythmGenerator import generateHarmonicRhythm
from schenkComposer.middlegroundGeneration.harmonyMarkovChain import HarmonyMarkovChain
from schenkComposer.utility import makeRomans

from music21.meter import TimeSignature
from music21.key import Key
from random import sample


def naiveMiddlegroundMelodyGenerator(harmonicProgression: list[RomanNumeral]) -> list[Note]:
    return [Note(sample(rn.pitchNames, 1)[0] + "4") for rn in harmonicProgression]


def smoothForwardMiddlegroundMelodyGenerator(
        harmonicProgression: list[RomanNumeral],
        possibleOctaves: tuple[int] = (3, 4, 5)
) -> list[Note]:
    firstNote = Note(sample(harmonicProgression[0].pitchNames, 1)[0] + str(sample(possibleOctaves, 1)[0]))
    notes = [firstNote]
    for i, harmony in enumerate(harmonicProgression[1:]):
        pitches = harmony.pitchNames
        possibleNotes = [findClosestOfPitch(notes[-1], p).nameWithOctave for p in pitches]
        closestNote = findClosestOfNotes(notes[-1].nameWithOctave, possibleNotes)
        notes.append(closestNote)
    return notes


def smoothBackwardMiddlegroundMelodyGenerator(
        harmonicProgression: list[RomanNumeral],
        possibleOctaves: tuple[int] = (5, 4),
        endOn: ChordMember = None
) -> list[Note]:
    firstOctave = str(sample(possibleOctaves, 1)[0])
    notes = []
    if endOn is None:
        notes.append(Note(sample(harmonicProgression[-1].pitchNames, 1)[0] + firstOctave))
    elif endOn is ChordMember.ROOT:
        notes.append(Note(harmonicProgression[-1].pitchNames[0] + firstOctave))
    elif endOn is ChordMember.THIRD:
        notes.append(Note(harmonicProgression[-1].pitchNames[1] + firstOctave))
    else:
        raise NotImplementedError()

    for i, harmony in enumerate(reversed(harmonicProgression[:-1])):
        pitches = harmony.pitchNames
        possibleNotes = [findClosestOfPitch(notes[-1], p).nameWithOctave for p in pitches]
        notes.append(findClosestOfNotes(notes[-1].nameWithOctave, possibleNotes))
    return list(reversed(notes))



def generateMiddlegroundMelodyForSection(
        timeSignature: TimeSignature = TimeSignature("4/4"),
        numMeasures: int = 4,
        phraseEnd: bool = True,
        endHarmony: str = "V",
        harmonyMarkovChain: HarmonyMarkovChain = HarmonyMarkovChain(),
        key: Key = Key("C"),
        endOn: ChordMember = None
):
    harmonicRhythm = generateHarmonicRhythm(timeSignature, numMeasures, phraseEnd=phraseEnd)
    harmony = harmonyMarkovChain.backwardsFromHarmony(endHarmony, length=len(harmonicRhythm))
    middlegroundMelody = smoothBackwardMiddlegroundMelodyGenerator(
        makeRomans(harmony, harmonicRhythm),
        endOn=endOn
    )
    harmony = makeRomans(harmony)
    for i, rhythm in enumerate(harmonicRhythm):
        harmony[i].quarterLength = rhythm
    return harmonicRhythm, harmony, middlegroundMelody


if __name__ == "__main__":
    hr, h, mm = generateMiddlegroundMelodyForSection()
    print(hr, h, mm)