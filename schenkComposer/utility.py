import music21.musicxml.m21ToXml
from multipledispatch import dispatch

from schenkComposer.music21Wrappers.note import Note
from schenkComposer.music21Wrappers.romanNumeral import RomanNumeral
from schenkComposer.music21Wrappers.scale import MajorScale, HarmonicMinorScale
from schenkComposer.contour.contour import Contour
from schenkComposer.contour.contourType import ContourType
from schenkComposer.foregroundGeneration.nht import NHT

from music21.interval import Interval
from music21.key import Key
from music21.scale import ConcreteScale
from music21.stream import Stream, Score, Part
from music21 import midi, stream, converter, instrument
from music21 import dynamics

from collections import defaultdict
from copy import deepcopy
import numpy as np
import json
from pprint import pprint


def checkMakerParams(quarterLengths, symbols):
    if len(symbols) != len(quarterLengths):
        raise ValueError(
            f"symbols and quarterLengths must be the same size. "
            f"Got {len(symbols)} and {len(quarterLengths)} instead"
        )


def makeRoman(rnKey: str = "C", symbol: str = "I", quarterLength: float = 1) -> RomanNumeral:
    k = Key(rnKey)
    rn = RomanNumeral(symbol)
    rn.quarterLength = quarterLength
    rn.key = k
    return rn


def makeRomanWithKey(rnKey: Key = Key("C"), symbol: str = "I", quarterLength: float = 1) -> RomanNumeral:
    rn = RomanNumeral(symbol)
    rn.quarterLength = quarterLength
    rn.key = rnKey
    return rn


def makeRomans(symbols: list[str], quarterLengths: list[float] = None, rnKey: str = "C") -> list[RomanNumeral]:
    if quarterLengths is None:
        quarterLengths = [1 for _ in range(len(symbols))]
    checkMakerParams(quarterLengths, symbols)
    return [makeRoman(rnKey, symbol, quarterlen) for symbol, quarterlen in zip(symbols, quarterLengths)]


def makeRomansWithKey(symbols: list[str], quarterLengths: list[float] = None, rnKey: Key = Key("C")) -> list[RomanNumeral]:
    if quarterLengths is None:
        quarterLengths = [1 for _ in range(len(symbols))]
    checkMakerParams(quarterLengths, symbols)
    return [makeRomanWithKey(rnKey, symbol, quarterlen) for symbol, quarterlen in zip(symbols, quarterLengths)]


def makeNotes(symbols: list[str], quarterLengths: list[float] = None) -> list[Note]:
    if quarterLengths is None:
        quarterLengths = [1 for _ in range(len(symbols))]
    checkMakerParams(quarterLengths, symbols)
    return [Note(s, quarterLength=q) for s, q in zip(symbols, quarterLengths)]


def findClosestOfNotes(fromNote: str, toNoteOptions: list[str]) -> Note:
    fromNote = Note(fromNote)
    distances = []
    for tn in toNoteOptions:
        toNote = Note(tn)
        interval = Interval(fromNote, toNote)
        distances.append(abs(interval.semitones))
    i = distances.index(min(distances))
    return Note(toNoteOptions[i])


def findClosestOfPitch(fromNote: Note, toPitch: str) -> Note:
    oct = fromNote.octave
    return findClosestOfNotes(
        fromNote.nameWithOctave,
        [
            toPitch + str(oct),
            toPitch + str(oct + 1),
            toPitch + str(oct - 1)
        ]
    )


def findClosestOfPitches(fromNote: Note, toPitches: list[str]) -> Note:
    oct = fromNote.octave
    options = [
        (
            toPitch + str(oct),
            toPitch + str(oct + 1),
            toPitch + str(oct - 1)
        ) for toPitch in toPitches
    ]
    return findClosestOfNotes(
        fromNote.nameWithOctave,
        [o for option in options for o in option]
    )


def contoursFromNotes(noteList: list[Note]) -> list[Contour]:
    contours = []
    for i in range(len(noteList) - 1):
        contours.append(contourBetween(noteList[i], noteList[i + 1]))
    return contours


def contourBetween(fromNote: Note, toNote: Note) -> Contour:
    interval = Interval(fromNote, toNote)
    if interval.semitones < 0:
        return Contour(ContourType.DOWN, 0)
    elif interval.semitones > 0:
        return Contour(ContourType.UP, 0)
    else:
        return Contour(ContourType.STRAIGHT, 0)


def findNearestNoteOfHarmonyAndRoughness(fromNote: Note, harmony: RomanNumeral, contour: Contour,
                                         roughness: int) -> Note:
    if contour.contourType is ContourType.STRAIGHT:
        return deepcopy(fromNote)

    # Get the notes of the harmony as midi numbers
    harmonyNotes = [p.midi % 12 for p in harmony.pitches]
    tryNote = Note(fromNote.pitch.midi)
    currRoughness = -1
    while currRoughness != roughness:
        if contour.contourType is ContourType.UP:
            tryNote = Note(tryNote.pitch.midi + 1)
        else:
            tryNote = Note(tryNote.pitch.midi - 1)
        if tryNote.pitch.midi % 12 in harmonyNotes:
            currRoughness += 1
    return tryNote


def findNearestNHTNote(fromNote: Note, harmony: RomanNumeral, contour: Contour, scale: ConcreteScale) -> Note:
    pitches = [p.name for p in scale.getPitches()][:-1]
    pitchClass = fromNote.pitch.name
    if contour.contourType is ContourType.UP:
        while pitchClass in harmony.pitchNames:
            fromPitchIndex = pitches.index(pitchClass)
            pitchClass = pitches[(fromPitchIndex + 1) % len(pitches)]
        return findClosestOfPitch(fromNote, pitchClass)
    elif contour.contourType is ContourType.DOWN:
        while pitchClass in harmony.pitchNames:
            fromPitchIndex = pitches.index(pitchClass)
            pitchClass = pitches[fromPitchIndex - 1]
        return findClosestOfPitch(fromNote, pitchClass)
    else:
        return deepcopy(fromNote)


def findPossibleNHTs(startNote: Note, endNote: Note, nhtOnStrong: bool) -> tuple[NHT]:
    interval = Interval(startNote, endNote)
    possibleNHTs = {NHT.ANTICIPATION}
    if abs(interval.semitones) in [3, 4]:
        possibleNHTs.add(NHT.PASSING)
    if interval.semitones >= 1:
        possibleNHTs.update([NHT.UPPER_INCOMPLETE])
    if interval.semitones >= 1 and not nhtOnStrong:
        possibleNHTs.update([NHT.LOWER_ESCAPE])
    if interval.semitones <= -1:
        possibleNHTs.update([NHT.LOWER_INCOMPLETE])
    if interval.semitones <= -1 and not nhtOnStrong:
        possibleNHTs.update([NHT.UPPER_ESCAPE])
    if interval.semitones == 0:
        possibleNHTs.update([NHT.UPPER_NEIGHBOR, NHT.LOWER_NEIGHBOR])
        possibleNHTs.remove(NHT.ANTICIPATION)
    if interval.semitones in [-1, -2] and nhtOnStrong:
        possibleNHTs.update([NHT.SUSPENSION])
    if interval.semitones in [1, 2] and nhtOnStrong:
        possibleNHTs.update([NHT.RETARDATION])

    return tuple(possibleNHTs)


def getContourType(startNote: Note, endNote: Note) -> ContourType:
    interval = Interval(startNote, endNote)
    if interval.semitones > 0:
        return ContourType.UP
    elif interval.semitones < 0:
        return ContourType.DOWN
    else:
        return ContourType.STRAIGHT


def productionsDictFromJSON(jsonPath: str):
    with open(jsonPath, "r") as f:
        data = json.load(f)

    answer = {}
    for lhs, rhs_ in data.items():
        counts = sum([info['count'] for info in rhs_])
        for info in rhs_:
            answer[f"{lhs}->{info['production']}"] = info['count'] / counts

    return answer


def checkCorrectContour(fromNote: Note, toNote: Note, correctContour: Contour):
    interval = Interval(fromNote, toNote)
    if interval.semitones > 0:
        return correctContour.contourType is ContourType.UP
    elif interval.semitones < 0:
        return correctContour.contourType is ContourType.DOWN
    else:
        return correctContour.contourType is ContourType.STRAIGHT


def noteListToMidi(noteList: list, filepath: str = None):
    s = Stream()
    for n in noteList:
        s.append(n)
    sp = midi.realtime.StreamPlayer(s)
    if filepath:
        s.write("midi", fp=filepath)
    sp.play()


def noteListHarmonyListToMidi(noteList: list, harmonyList: list, filepath: str = None):
    s = Stream()
    ns = Stream()
    hs = Stream()
    for n in noteList:
        ns.append(n)
    for h in harmonyList:
        for p in h.pitches:
            p.octave = 3
        hs.append(h)
    hs.insert(0, dynamics.Dynamic('p'))
    s.insert(ns)
    s.insert(hs)
    sp = midi.realtime.StreamPlayer(s)
    if filepath:
        s.write("midi", fp=filepath)
    sp.play()


def noteListHarmonyListToScore(noteList: list, harmonyList: list, filepath: str = None):
    s = Stream()
    ns = Stream()
    hs = Stream()
    for n in noteList:
        ns.append(n)
    for h in harmonyList:
        for p in h.pitches:
            p.octave = 3
        hs.append(h)
    hs.insert(0, dynamics.Dynamic('p'))
    s.insert(0, ns)
    s.insert(0, hs)
    if filepath:
        s.write("musicxml", fp=filepath)


def loadMidi(midiPath: str, outPath: str):
    score = converter.parse(midiPath)
    for el in score.recurse():
        if 'Instrument' in el.classes:
            el.activeSite.replace(el, instrument.Piano())
    for el in score[0].recurse():
        if 'Note' in el.classes:
            el.octave += 1
    for el in score[1].recurse():
        if 'Note' in el.classes:
            el.octave -= 1
    score[1].insert(0, dynamics.Dynamic('p'))
    score[2].insert(0, dynamics.Dynamic('p'))
    score[0].insert(0, dynamics.Dynamic('f'))
    # score.show("text")
    # sp = midi.realtime.StreamPlayer(score)
    # sp.play()
    score.write("midi", fp=outPath)


def parseRhythmsToQuarterLengths(rhythms: list[str]):
    dic = {
        '𝅘𝅥𝅰': 0.125,
        '𝅘𝅥𝅰.': 0.1875,
        '𝅘𝅥𝅯': 0.25,
        '𝅘𝅥𝅯.': 0.375,
        '𝅘𝅥𝅮': 0.5,
        '𝅘𝅥𝅮.': 0.75,
        '♩': 1.0,
        '♩.': 1.5,
        '𝅗𝅥': 2.0,
        '𝅗𝅥.': 3.0,
        '𝅝': 4.0,
        '𝅝.': 6.0
    }
    return [dic[rhythm] for rhythm in rhythms]



if __name__ == "__main__":
    # noteListHarmonyListToMidi(
    #     [Note("C4"), Note("D4"), Note("E4")],
    #     makeRomans(["I", "V", "I"], [1, 1, 1])
    # )
    j = 1
    for i in range(4, 25):
        try:
            loadMidi(
                f"C:/Users/88ste/OneDrive/Documents/GitHub/schenkComposer/flowMachines/raw/FlowMachinesSong {i}.mid",
                f"C:/Users/88ste/OneDrive/Documents/GitHub/schenkComposer/flowMachines/normalized/fm{j}.mid",
            )
            j += 1
        except Exception as e:
            print(e)
