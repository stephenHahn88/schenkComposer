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
from schenkComposer.foregroundGeneration.foregroundRhythmGenerator import generateForegroundRhythm
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


@app.route("/model/harmonic-progression/<string:endHarmony>/<int:length>/<string:transitionMatrix>")
def generateHarmony(endHarmony, length, transitionMatrix):
    parsedMatrix = transitionMatrix.split("-")
    parsedMatrix = np.array([[int(parsedMatrix[(i*7)+j]) for j in range(7)] for i in range(7)])
    print(parsedMatrix)
    hmc = HarmonyMarkovChain(parsedMatrix.transpose())  # TODO: get matrix from database
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
    mgMelody = [Note(n) for n in mgMelody.split("-")]
    fgRhythm = [tuple(parseRhythmsToQuarterLengths([r.strip() for r in rhythm.split("s")])) for rhythm in fgRhythm.split("-")]
    mgRhythm = parseRhythmsToQuarterLengths([note.strip() for measure in mgRhythm.split("-") for note in measure.split("s")])
    mgHarmony = makeRomans([harmony.strip() for harmony in mgHarmony.split("-")], mgRhythm)

    notes, harmony = generateForegroundMelodyUntilValid(
        middlegroundMelody=mgMelody,
        foregroundRhythm=fgRhythm,
        middlegroundHarmonicRhythm=mgRhythm,
        middlegroundHarmony=mgHarmony
    )
    print(notes, harmony)
    notes = [str(n) for n in notes]
    harmony = [tuple([f"{p.nameWithOctave[0] + '3'}: {h.quarterLength}" for p in h.pitches]) for h in harmony]

    return {"notes": notes, "harmony": harmony}

if __name__ == "__main__":
    app.run(port=8888, debug=True)

