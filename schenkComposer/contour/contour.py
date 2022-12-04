from schenkComposer.contour.contourType import ContourType
from multipledispatch import dispatch


class Contour:
    """
    Describes a directional contour between two notes
    along with the number of notes between the notes
    """

    @dispatch(ContourType, int, bool)
    def __init__(self, contourType: ContourType, numBetween: int = 1, toNHT: bool = False):
        self.contourType = contourType
        self.numBetween = numBetween
        self.toNHT = toNHT

    @dispatch(ContourType, int)
    def __init__(self, contourType: ContourType, numBetween: int = 1):
        self.__init__(contourType, numBetween, False)

    @dispatch(str, int, bool)
    def __init__(self, contourType: str, numBetween: int, toNHT: bool = False):
        """For ease of generation, using string instead of enum"""
        ct = contourType.lower()
        if ct in ["up", "u", "↗"]:
            self.__init__(ContourType.UP, numBetween, toNHT)
        elif ct in ["down", "d", "↘"]:
            self.__init__(ContourType.DOWN, numBetween, toNHT)
        elif ct in ["straight", "s", "→"]:
            self.__init__(ContourType.STRAIGHT, numBetween, toNHT)
        else:
            raise ValueError("improper contour type")

    @dispatch(str)
    def __init__(self, contourType: str):
        """For ease of generation, contourType includes '_' if it heads to NHT"""
        if contourType[-1] == "_":
            self.__init__(contourType[0], int(contourType[1:-1]), True)
        else:
            self.__init__(contourType[0], int(contourType[1:]), False)

    def __str__(self):
        sub = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        sub2 = str.maketrans("NHT()", "ᴺᴴᵀ⁽⁾")
        return f"{self.contourType.value[0]}" \
               f"{str(self.numBetween).translate(sub)}" \
               f"{'(NHT)'.translate(sub2) if self.toNHT else ''}"

    def setNumBetween(self, num: int):
        self.numBetween = num

if __name__ == "__main__":
    c = Contour("s1_")
    print(str(c))
