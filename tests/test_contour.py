import pytest
from schenkComposer.contour.contour import Contour
from schenkComposer.contour.contourType import ContourType

def test_init():
    up = Contour(ContourType.UP, 3)
    down = Contour(ContourType.DOWN, 2)
    straight = Contour(ContourType.STRAIGHT, 5)

    assert up.contourType == ContourType.UP
    assert up.numBetween == 3
    assert down.contourType == ContourType.DOWN
    assert down.numBetween == 2
    assert straight.contourType == ContourType.STRAIGHT
    assert straight.numBetween == 5