import pytest
from src.utils.astropi_utils import hex_to_degrees, degrees_to_hex


@pytest.mark.parametrize("degrees, hex_str, precise", [
    (26.4441, "12CE", False),
    (74.0643, "34AB", False),
    (0.0, "0000", False),
    (180.0, "8000", False),
    (359.9945, "FFFF", False),
    (270.0, "C000", False),
    (38.04257831, "1B0D70A6", True),
    (89.25909701, "3F791F6B", True),
    (38.04256439, "1B0D7000", True),
    (89.25908804, "3F791F00", True),
    (0.0, "00000000", True),
    (180.0, "80000000", True),
    (359.99999992, "FFFFFFFF", True),
    (321.95743561, "E4F29000", True),
    (119.99999997, "55555555", True),
])
def test_hex_to_degrees(degrees, hex_str, precise):
    assert hex_to_degrees(hex_str, precise) == degrees


@pytest.mark.parametrize("degrees, hex_str, precise", [
    (26.4441, "12CE", False),
    (74.0643, "34AB", False),
    (0.0, "0000", False),
    (180.0, "8000", False),
    (359.9945, "FFFF", False),
    (360.0, "0000", False),
    (-90.0, "C000", False),
    (38.04257831, "1B0D70A6", True),
    (89.25909701, "3F791F6B", True),
    (38.04256439, "1B0D7000", True),
    (89.25908804, "3F791F00", True),
    (0.0, "00000000", True),
    (180.0, "80000000", True),
    (359.99999992, "FFFFFFFF", True),
    (360.0, "00000000", True),
    (-38.04256439, "E4F29000", True),
    (480, "55555555", True),
])
def test_degrees_to_hex(degrees, hex_str, precise):
    assert degrees_to_hex(degrees, precise) == hex_str

