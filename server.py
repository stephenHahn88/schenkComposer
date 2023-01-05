from random import sample, choices
from string import ascii_letters, digits
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

import flask
from flask import Flask, Response, request
import json
from copy import deepcopy
from pymongo import MongoClient
import numpy as np
from music21.meter import TimeSignature
import hashlib

from schenkComposer.form.phraseGenerator import generatePhrase
from schenkComposer.foregroundGeneration.foregroundMelodyGenerator import generateForegroundMelodyUntilValid
from schenkComposer.middlegroundGeneration.presetTransitionMatrices import presetCollection
from schenkComposer.middlegroundGeneration.harmonyMarkovChain import HarmonyMarkovChain
from schenkComposer.middlegroundGeneration.middlegroundMelodyGenerator import smoothBackwardMiddlegroundMelodyGenerator
from schenkComposer.foregroundGeneration.stockRhythms import meters

from schenkComposer.utility import makeRomans, parseRhythmsToQuarterLengths
from schenkComposer.music21Wrappers.note import Note

app = Flask(__name__)

# client = AsyncIOMotorClient('localhost', 27017)
client = MongoClient('localhost', 27017)

"""API HELPERS"""


def _getMel(composerId: str, melodyId: str):
    db = client["test"]
    melodies = db["melodies"]
    mel = melodies.find({"composerId": composerId, "melodyId": melodyId})
    mel = list(mel)
    if len(mel) == 0:
        return "404"
    return mel[0]


def _determineStatus(composerId: str, melodyId: str, mel, component):
    if str(mel) == '404':
        return {"status": 404, "result": {"composerId": composerId, "melodyId": melodyId}}
    try:
        test = mel[component]
    except KeyError:
        return {"status": 404, "result": {"composerId": composerId, "melodyId": melodyId}}
    return {"status": 200, "result": mel[component]}


def _putComponent(composerId: str, melodyId: str, setObj):
    db = client["test"]
    melodies = db["melodies"]
    return melodies.update_one(
        {
            "composerId": composerId,
            "melodyId": melodyId
        },
        {
            "$set": setObj
        },
        True
    )


"""API SAVE MELODY PARAMETER ROUTES"""

"""GET ROUTES"""


@app.route("/api/composer/<composerId>")
def getAllMelodies(composerId):
    db = client["test"]
    melodies = db["melodies"]
    mels = list(melodies.find({"composerId": composerId}))
    if len(mels) == 0:
        return Response("No composer found", status=404)
    return json.dumps(mels)


@app.route("/api/composer/<composerId>/melody/<melodyId>/phrase-structure")
def getPhraseStructure(composerId, melodyId):
    print("hi")
    mel = _getMel(composerId, melodyId)
    print(mel)
    result = _determineStatus(composerId, melodyId, mel, "phraseStructure")
    return json.dumps(result["result"])

@app.route("/api/composer/<composerId>/melody/<melodyId>/meter")
def getMeter(composerId, melodyId):
    mel = _getMel(composerId, melodyId)
    result = _determineStatus(composerId, melodyId, mel, "meter")
    return json.dumps(result["result"])


@app.route("/api/composer/<composerId>/melody/<melodyId>/hypermeter")
def getHypermeter(composerId, melodyId):
    mel = _getMel(composerId, melodyId)
    result = _determineStatus(composerId, melodyId, mel, "hypermeter")
    return json.dumps(result["result"])


@app.route("/api/composer/<composerId>/melody/<melodyId>/mg-rhythm")
def getMgRhythm(composerId, melodyId):
    mel = _getMel(composerId, melodyId)
    result = _determineStatus(composerId, melodyId, mel, "mgRhythm")
    return json.dumps(result["result"])


@app.route("/api/composer/<composerId>/melody/<melodyId>/fg-rhythm")
def getFgRhythm(composerId, melodyId):
    mel = _getMel(composerId, melodyId)
    result = _determineStatus(composerId, melodyId, mel, "fgRhythm")
    return json.dumps(result["result"])


@app.route("/api/composer/<composerId>/melody/<melodyId>/matrix")
def getMatrix(composerId, melodyId):
    mel = _getMel(composerId, melodyId)
    resultMatrix = _determineStatus(composerId, melodyId, mel, "transitionMatrix")
    resultLabels = _determineStatus(composerId, melodyId, mel, "transitionLabels")
    resultOpen = _determineStatus(composerId, melodyId, mel, "openHarmonies")
    resultClose = _determineStatus(composerId, melodyId, mel, "closeHarmonies")
    result = {
        "matrix": resultMatrix['result'],
        "labels": resultLabels['result'],
        "openHarmonies": resultOpen['result'],
        "closeHarmonies": resultClose['result']
    }
    return json.dumps(result)


@app.route("/api/composer/<composerId>/melody/<melodyId>/harmonicProgression")
def getHarmonicProgression(composerId, melodyId):
    mel = _getMel(composerId, melodyId)
    result = _determineStatus(composerId, melodyId, mel, "harmonicProgression")
    return json.dumps(result["result"])


@app.route("/api/composer/<composerId>/melody/<melodyId>/middleground-melody")
def getMgMelody(composerId, melodyId):
    mel = _getMel(composerId, melodyId)
    result = _determineStatus(composerId, melodyId, mel, "mgMelody")
    return json.dumps(result["result"])


"""PUT ROUTES"""


@app.route("/api/composer/<composerId>/melody/<melodyId>/phrase-structure", methods=['PUT'])
def putPhraseStructure(composerId, melodyId):
    result = _putComponent(composerId, melodyId, request.get_json())
    return {"status": 200}


@app.route("/api/composer/<composerId>/melody/<melodyId>/hypermeter", methods=['PUT'])
def putHypermeter(composerId, melodyId):
    result = _putComponent(composerId, melodyId, request.get_json())
    return {"status": 200}


@app.route("/api/composer/<composerId>/melody/<melodyId>/meter", methods=['PUT'])
def putMeter(composerId, melodyId):
    result = _putComponent(composerId, melodyId, request.get_json())
    return {"status": 200}


@app.route("/api/composer/<composerId>/melody/<melodyId>/mg-rhythm", methods=['PUT'])
def putMgRhythm(composerId, melodyId):
    result = _putComponent(composerId, melodyId, request.get_json())
    return {"status": 200}


@app.route("/api/composer/<composerId>/melody/<melodyId>/fg-rhythm", methods=['PUT'])
def putFgRhythm(composerId, melodyId):
    result = _putComponent(composerId, melodyId, request.get_json())
    return {"status": 200}


@app.route("/api/composer/<composerId>/melody/<melodyId>/matrix", methods=['PUT'])
def putMatrix(composerId, melodyId):
    result = _putComponent(composerId, melodyId, request.get_json())
    return {"status": 200}


@app.route("/api/composer/<composerId>/melody/<melodyId>/harmonicProgression", methods=['PUT'])
def putHarmonicProgression(composerId, melodyId):
    result = _putComponent(composerId, melodyId, request.get_json())
    return {"status": 200}


@app.route("/api/composer/<composerId>/melody/<melodyId>/middleground-melody", methods=['PUT'])
def putMgMelody(composerId, melodyId):
    result = _putComponent(composerId, melodyId, request.get_json())
    return {"status": 200}


"""API LOGIN AND USER CREATION"""


@app.route("/api/user-exists/<username>")
def getUserExists(username):
    db = client["test"]
    users = db["users"]

    user = list(users.find({"username": username}))
    if len(user) == 0:
        return {"status": "not found"}
    return {"status": "ok"}


@app.route("/api/login-info/<username>/<password>")
def getLoginInfo(username, password):
    db = client["test"]
    users = db["users"]

    user = list(users.find({"username": username}))
    if len(user) == 0:
        return {"status": "not found"}
    user = user[0]

    passwordHash = user["passwordHash"]
    passwordSalt = user["passwordSalt"]

    passwordSalted = password + passwordSalt
    givenHash = hashlib.sha256(passwordSalted.encode()).hexdigest()
    if givenHash != passwordHash:
        return {"status": "unauthorized"}

    composerId = user["composerId"]
    return {"composerId": composerId, "status": 200}


@app.route("/api/create-user", methods=["PUT"])
def putUser():
    db = client["test"]
    users = db["users"]

    json = request.get_json()
    username = json["username"]
    password = json["password"]

    salt = ''.join(choices(ascii_letters + digits, k=32))
    passwordSalted = password + salt
    passHash = hashlib.sha256(passwordSalted.encode()).hexdigest()

    idSalt = ''.join(choices(ascii_letters + digits, k=8))
    usernameSalted = username + idSalt
    idHash = hashlib.sha256(usernameSalted.encode()).hexdigest()

    result = users.insert_one({
        "username": username,
        "passwordHash": passHash,
        "passwordSalt": salt,
        "composerId": idHash,
        "idSalt": idSalt
    })
    return {"status": 200}


@app.route("/api/create-melody", methods=["PUT"])
def putMelody():
    db = client["test"]
    db["melodies"].insert_one(request.get_json())
    return {"status": 200}


"""MODEL GENERATION ROUTES"""


# Generates single subphrase from scratch
@app.route("/api/generate-all")
def generateAll():
    notes, harmony = generateForegroundMelodyUntilValid()
    notes = [str(n) for n in notes]
    harmony = [tuple([f"{p.nameWithOctave[0] + '3'}: {h.quarterLength}" for p in h.pitches]) for h in harmony]
    print(notes)
    print(harmony)
    # noteListHarmonyListToMidi(notes, harmony)
    return json.dumps({"notes": notes, "harmonies": harmony})


# Get matrix of provided name
@app.route("/api/matrix/<matrixName>")
def generateMatrix(matrixName):
    matrix = deepcopy(presetCollection[matrixName])
    matrix["matrix"] = matrix["matrix"].tolist()
    print(matrix)
    return matrix


# Generate harmonic sequence with given end, length, matrix, and labels
@app.route("/api/harmonic-progression/<endHarmony>/<int:length>/<transitionMatrix>/<transitionLabels>")
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


# Generate a random phrase structure
@app.route("/api/phrase-structure")
def generatePhraseStructure():
    phrase = generatePhrase()
    print(phrase)
    return {"phrase": phrase}


# Generate smooth middleground given a harmonic progression
@app.route("/api/middleground-melody/<string:harmonicProgression>")
def generateMiddlegroundMelody(harmonicProgression):
    parsedHarmony = harmonicProgression.split("-")
    romans = makeRomans(parsedHarmony)
    notes = smoothBackwardMiddlegroundMelodyGenerator(romans)
    notes = [f"{note.pitch.name}/{note.pitch.octave}" for note in notes]
    print(notes)
    return {"mgNotes": notes}


# Generate foreground rhythm with time signature and middleground rhythm
@app.route("/api/foreground-rhythm/<string:time>/<string:mgRhythm>")
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


# Generate melody using all possible parameters
@app.route("/api/generate-melody/<string:mgMelody>/<string:fgRhythm>/<string:mgRhythm>/<string:mgHarmony>")
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


# Generate melody without foreground rhythm and middleground melody
@app.route("/api/generate-melody/partial/<string:meter>/<string:mgRhythm>/<string:mgHarmony>")
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


"""GENERATION HELPERS"""

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
    # melodies.insert_one({'hi': 'hello'})
    app.run(port=8888, debug=True)
