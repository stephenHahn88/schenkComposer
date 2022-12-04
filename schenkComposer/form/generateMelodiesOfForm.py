from schenkComposer.foregroundGeneration.foregroundMelodyGenerator import generateForegroundMelodyUntilValid
from schenkComposer.middlegroundGeneration.chordMember import ChordMember
from schenkComposer.utility import noteListHarmonyListToMidi, noteListToMidi, noteListHarmonyListToScore
from schenkComposer.music21Wrappers.note import Note
from time import strftime, gmtime

from schenkComposer.utility import makeRoman
from copy import deepcopy


def generateSentence():
    a, h1 = generateForegroundMelodyUntilValid(phraseEnd=False, endHarmony="V", numMeasures=2)
    b, h2 = generateForegroundMelodyUntilValid(phraseEnd=True, endHarmony="IV", numMeasures=2)
    c, h3 = generateForegroundMelodyUntilValid(phraseEnd=True, endHarmony="I", numMeasures=4, endOn=ChordMember.THIRD)
    # a2 = deepcopy(a[:-1]) + [Note("D5", quarterLength=4)]
    # h2 = deepcopy(h1[:-1]) + [makeRoman("C", "V", quarterLength=4)]
    # noteListToMidi(a + a2 + c, f"../generatedMelodies/mel_only/sentence{strftime('%H_%M_%S', gmtime())}.mid")
    noteListHarmonyListToScore(a+b+c, h1+h2+h3, f"../generatedMelodies/score/sentence{strftime('%H_%M_%S', gmtime())}.xml")
    # noteListHarmonyListToMidi(a+a2+c, h1+h2+h3, f"../generatedMelodies/sentence{strftime('%H_%M_%S', gmtime())}.mid")
    # return a+a2+c, h1+h2+h3

def generatePeriod():
    # a, h1 = generateForegroundMelodyUntilValid(phraseEnd=False, endHarmony="IV", numMeasures=4)
    a2, h2 = generateForegroundMelodyUntilValid(phraseEnd=True, endHarmony="V", numMeasures=4)
    # b, h3 = generateForegroundMelodyUntilValid(phraseEnd=False, endHarmony="IV", numMeasures=4)
    b2, h4 = generateForegroundMelodyUntilValid(phraseEnd=True, endHarmony="I", numMeasures=4, endOn=ChordMember.ROOT)
    # a, h1 = generateSentence()
    # b, h2 = generateForegroundMelodyUntilValid(phraseEnd=True, endHarmony="I", numMeasures=8, endOn=ChordMember.ROOT)

    # noteListToMidi(a+b, f"../generatedMelodies/mel_only/period{strftime('%H_%M_%S', gmtime())}.mid")
    # noteListHarmonyListToMidi(a+b, h1+h2, f"../generatedMelodies/period{strftime('%H_%M_%S', gmtime())}.mid")
    noteListHarmonyListToScore(a2+b2, h2+h4, f"../generatedMelodies/score/sentence{strftime('%H_%M_%S', gmtime())}.xml")


if __name__ == "__main__":
    # generateSentence()
    generatePeriod()

