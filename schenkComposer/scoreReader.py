import music21
from music21 import converter, configure


class ScoreReader:
    def __init__(self):
        self.currScore = None

    @staticmethod
    def print(music21Obj):
        music21Obj.show("text")

    def getTimeSignature(self):
        for el in self.currScore.flatten():
            if type(el) is music21.meter.TimeSignature:
                return el

    def parse(self, filepath: str, fileFormat: str = None):
        if fileFormat is None:
            self.currScore = converter.parse(filepath)
        else:
            self.currScore = converter.parse(filepath, format=fileFormat)

    def parseMeasureRhythms(self):
        if self.currScore is None:
            raise Exception("Must call 'parse' to load a score before calling other functions")

        timeSignature = self.getTimeSignature()

        rhythms = set()
        currRhythm = []
        for el in self.currScore.parts[0].flatten():
            if type(el) is not music21.note.Note and type(el) is not music21.note.Rest:
                continue
            if el.beat == 1:
                rhythms.add(" ".join(currRhythm)) if currRhythm else 0
                currRhythm = []
            if type(el) is music21.note.Note:
                currRhythm.append(f"n-{el.beat}")
            if type(el) is music21.note.Rest:
                currRhythm.append(f"r-{el.beat}")

        print(rhythms)

if __name__ == "__main__":
    sr = ScoreReader()
    sr.parse("./testFugue.mxl")
    # configure.run()
    sr.parseMeasureRhythms()






