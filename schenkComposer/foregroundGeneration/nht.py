from enum import Enum


class NHT(Enum):
    PASSING = ("P", 1)

    UPPER_NEIGHBOR = ("UN", 1)
    LOWER_NEIGHBOR = ("LN", 1)
    UPPER_INCOMPLETE = ("UIN", 1)
    LOWER_INCOMPLETE = ("LIN", 1)

    UPPER_ESCAPE = ("UE", 1)
    LOWER_ESCAPE = ("LE", 1)

    SUSPENSION = ("S", 1)
    RETARDATION = ("R", 1)
    ANTICIPATION = ("A", 1)