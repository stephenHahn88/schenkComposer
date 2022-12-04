import music21.scale

from schenkComposer.foregroundGeneration.foregroundMelodyGenerator import generateForegroundMelodyUntilValid
from schenkComposer.middlegroundGeneration import harmonyMarkovChain, presetTransitionMatrices
from schenkComposer.middlegroundGeneration.chordMember import ChordMember
from schenkComposer.utility import noteListHarmonyListToMidi
from time import strftime, gmtime

from music21.scale import ConcreteScale
from music21.key import Key

def main(
        rhythms: dict,
        matrix, labels,
        endPhrase1,
        endPhrase2,
        scale: ConcreteScale,
        savePath,
        includeNHT: bool = True,
        possibleHarmonicRhythms: list = None
):
    hmc = harmonyMarkovChain.HarmonyMarkovChain(matrix, labels)

    n1, h1 = generateForegroundMelodyUntilValid(
        harmonyMarkovChain=hmc,
        stockRhythms=rhythms,
        endHarmony=endPhrase1,
        scale=scale,
        key=Key(scale.tonic),
        includeNHT=includeNHT,
        possibleHarmonicRhythms=possibleHarmonicRhythms
    )
    n2, h2 = generateForegroundMelodyUntilValid(
        harmonyMarkovChain=hmc,
        stockRhythms=rhythms,
        endHarmony=endPhrase2,
        scale=scale,
        key=Key(scale.tonic),
        includeNHT=includeNHT,
        possibleHarmonicRhythms=possibleHarmonicRhythms
    )
    notes = n1+n2
    harmonies = h1+h2
    print(notes)
    print(harmonies)

    noteListHarmonyListToMidi(
        notes,
        harmonies,
        f"C:/Users/88ste/OneDrive/Documents/"
        f"GitHub/schenkComposer/style_experiment/{savePath}")

def rock_generator():
    rock = presetTransitionMatrices.ROCK_TRANSITION_MATRIX
    main(
        {
            "4/4": {  # Rock
                1: ((1,), (2 / 3, 1 / 3)),
                1.5: ((1.5,), (1, 0.5), (0.5, 0.5, 0.5)),
                2: ((2,), (0.75, 0.75, 0.5), (1.5, 0.5)),
                3: ((1.5, 1, 0.5), (1, 1.5, 0.5)),
                4: ((4,), (0.5, 1, 1, 1, 0.5), (1.5, 1, 1, 0.5))
            }
        },
        rock["matrix"],
        rock["labels"],
        "IV",
        "I",
        ConcreteScale(pitches=["C4","D4","E4","F4","G4","A4","B4","C5"]),
        f"rock/rock_{strftime('%H_%M_%S', gmtime())}"
    )

def pentatonic_generator():
    scale = ConcreteScale(pitches=["C4", "D4", "E4", "G4", "A4"])
    pentatonic = presetTransitionMatrices.CHINESE_TRANSITION_MATRIX
    main(
        {
            "4/4": {
                1: ((1,), (0.5, 0.5)),
                2: ((2,), (1, 1), (1, 0.5, 0.5), (0.5, 0.5, 0.5, 0.5)),
                3: ((2, 0.5, 0.5), (0.5, 0.5, 0.5, 0.5, 0.5, 0.5)),
                4: ((4,), (2, 2), (1, 1, 1, 1))
            }
        },
        pentatonic["matrix"],
        pentatonic["labels"],
        "V[no3]",
        "I",
        scale,
        f"pentatonic/pentatonic_{strftime('%H_%M_%S', gmtime())}",
        includeNHT=True
    )

def gagaku_generator():
    scale = ConcreteScale(tonic="D4", pitches=[
        "D4", "E4",
        # "F4", "G4",
        "A4", "B4",
        # "C4",
        "D5"
    ])
    gagaku = presetTransitionMatrices.GAGAKU_TRANSITION_MATRIX
    main(
        {
            "4/4": {
                4: ((4,),),
                8: ((8,), (4, 4)),
                16: ((16,), (8, 8), (8, 4, 4), (4, 4, 4, 4))
            }
        },
        gagaku["matrix"],
        gagaku["labels"],
        "I[no5][add2][add6][add7]",
        "I[no5][add2][add6][add7]",
        scale,
        f"gagaku/gagaku_{strftime('%H_%M_%S', gmtime())}",
        possibleHarmonicRhythms=[(4,), (8,), (16,), (8, 8)],
        includeNHT=False
    )

if __name__ == "__main__":
    gagaku_generator()