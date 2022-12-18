from random import sample

from flask import Flask
import json
from copy import deepcopy
from pymongo import MongoClient
import numpy as np
from music21.meter import TimeSignature

from schenkComposer.form.phraseGenerator import generatePhrase
from schenkComposer.foregroundGeneration.foregroundMelodyGenerator import generateForegroundMelodyUntilValid
from schenkComposer.middlegroundGeneration.presetTransitionMatrices import presetCollection
from schenkComposer.middlegroundGeneration.harmonyMarkovChain import HarmonyMarkovChain
from schenkComposer.middlegroundGeneration.middlegroundMelodyGenerator import smoothBackwardMiddlegroundMelodyGenerator
from schenkComposer.foregroundGeneration.stockRhythms import meters

from schenkComposer.utility import makeRomans, parseRhythmsToQuarterLengths
from schenkComposer.music21Wrappers.note import Note

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.test
melodies = db.melodies


@app.route("/model/generate-all")
def generateAll():
    notes, harmony = generateForegroundMelodyUntilValid()
    notes = [str(n) for n in notes]
    harmony = [tuple([f"{p.nameWithOctave[0] + '3'}: {h.quarterLength}" for p in h.pitches]) for h in harmony]
    print(notes)
    print(harmony)
    # noteListHarmonyListToMidi(notes, harmony)
    return json.dumps({"notes": notes, "harmonies": harmony})


@app.route("/model/matrix/<matrixName>")
def getMatrix(matrixName):
    matrix = deepcopy(presetCollection[matrixName])
    matrix["matrix"] = matrix["matrix"].tolist()
    print(matrix)
    return matrix


@app.route("/model/harmonic-progression/<endHarmony>/<int:length>/<transitionMatrix>/<transitionLabels>")
def generateHarmony(endHarmony: str, length: int, transitionMatrix: str, transitionLabels: str):
    parsedLabels = transitionLabels.split("-")
    numLabels = len(parsedLabels)
    parsedMatrix = transitionMatrix.split("-")
    parsedMatrix = np.array([[int(parsedMatrix[(i * numLabels) + j]) for j in range(numLabels)] for i in range(numLabels)])
    print(parsedMatrix)
    hmc = HarmonyMarkovChain(parsedMatrix.transpose(), parsedLabels)
    progression = hmc.backwardsFromHarmony(endHarmony, length)
    print(progression)
    return {"progression": progression}


@app.route("/model/phrase-structure")
def generatePhraseStructure():
    phrase = generatePhrase()
    print(phrase)
    return {"phrase": phrase}


@app.route("/model/middleground-melody/<string:harmonicProgression>")
def generateMiddlegroundMelody(harmonicProgression):
    parsedHarmony = harmonicProgression.split("-")
    romans = makeRomans(parsedHarmony)
    notes = smoothBackwardMiddlegroundMelodyGenerator(romans)
    notes = [f"{note.pitch.name}/{note.pitch.octave}" for note in notes]
    print(notes)
    return {"mgNotes": notes}


@app.route("/model/foreground-rhythm/<string:time>/<string:mgRhythm>")
def generateForegroundRhythm(time: str, mgRhythm: str):
    timeSignature = TimeSignature("/".join(time.split("-")))
    rhythm = mgRhythm.split("-")
    rhythm = parseRhythmsToQuarterLengths(rhythm)
    meter = f"{timeSignature.numerator}/{timeSignature.denominator}"
    foregroundRhythm = []
    for r in rhythm:
        options = meters[meter][r]
        foregroundRhythm.append(sample(options, k=1)[0])
    print(foregroundRhythm)
    return {"fgRhythm": foregroundRhythm}


@app.route("/model/generate-melody/<string:mgMelody>/<string:fgRhythm>/<string:mgRhythm>/<string:mgHarmony>")
def generateMelody(mgMelody, fgRhythm, mgRhythm, mgHarmony):
    mgMelody = _mgMelodyParser(mgMelody)
    fgRhythm = _fgRhythmParser(fgRhythm)
    mgRhythm = _mgRhythmParser(mgRhythm)
    mgHarmony = _mgHarmonyParser(mgHarmony, mgRhythm)

    notes, harmony = generateForegroundMelodyUntilValid(
        middlegroundMelody=mgMelody,
        foregroundRhythm=fgRhythm,
        middlegroundHarmonicRhythm=mgRhythm,
        middlegroundHarmony=mgHarmony
    )
    print(notes, harmony)
    notes, harmony = _prepareNotesHarmoniesReturn(notes, harmony)

    return {"notes": notes, "harmony": harmony}


@app.route("/model/generate-melody/partial/<string:meter>/<string:mgRhythm>/<string:mgHarmony>")
def generateMelodyWithoutForeground(meter, mgRhythm, mgHarmony):
    mgRhythm = _mgRhythmParser(mgRhythm)
    mgHarmony = _mgHarmonyParser(mgHarmony, mgRhythm)

    notes, harmony = generateForegroundMelodyUntilValid(
        middlegroundHarmony=mgHarmony,
        middlegroundHarmonicRhythm=mgRhythm
    )

    print(notes, harmony)
    notes, harmony = _prepareNotesHarmoniesReturn(notes, harmony)
    return {"notes": notes, "harmony": harmony}


###### HELPERS ######

def _mgMelodyParser(mgMelody):
    return [Note(n) for n in mgMelody.split("-")]


def _fgRhythmParser(fgRhythm):
    return [tuple(parseRhythmsToQuarterLengths([r.strip() for r in rhythm.split("s")])) for rhythm in
            fgRhythm.split("-")]


def _mgRhythmParser(mgRhythm):
    return parseRhythmsToQuarterLengths(
        [note.strip() for measure in mgRhythm.split("-") for note in measure.split("s")])


def _mgHarmonyParser(mgHarmony, mgRhythm):
    return makeRomans([harmony.strip() for harmony in mgHarmony.split("-")], mgRhythm)


def _prepareNotesHarmoniesReturn(notes, harmony):
    notes = [str(n) for n in notes]
    harmony = [tuple([f"{p.nameWithOctave[0] + '3'}: {h.quarterLength}" for p in h.pitches]) for h in harmony]
    return notes, harmony


if __name__ == "__main__":
    app.run(port=8888)
