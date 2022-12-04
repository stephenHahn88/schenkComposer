from music21.scale import MajorScale as ms
from music21.scale import HarmonicMinorScale as hms


class MajorScale(ms):
    diatonicToChromatic = {
        1: 0,
        2: 2,
        3: 4,
        4: 5,
        5: 7,
        6: 9,
        7: 11
    }
    chromaticToDiatonic = {v: k for k, v in diatonicToChromatic.items()}

    def getChromaticScaleDegreeFromPitch(self, pitchTarget):
        diatonicSD = self.getScaleDegreeFromPitch(pitchTarget)
        return self.diatonicToChromatic[diatonicSD]

    def getChromaticNumbers(self):
        return self.chromaticToDiatonic.keys()

    def getChromaticPitches(self):
        nums = self.getChromaticNumbers()
        self.getTonic()


class HarmonicMinorScale(hms):
    def getChromaticScaleDegreeFromPitch(self, pitchTarget):
        diatonicSD = self.getScaleDegreeFromPitch(pitchTarget)
        diatonicToChromatic = {
            1: 0,
            2: 2,
            3: 3,
            4: 5,
            5: 7,
            6: 8,
            7: 11
        }
        return diatonicToChromatic[diatonicSD]

    @staticmethod
    def getChromaticNumbers():
        return 0, 2, 3, 5, 7, 8, 11










