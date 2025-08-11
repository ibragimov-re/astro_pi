import pytest
from src.utils.coords import hex_to_degrees, degrees_to_hex


@pytest.mark.parametrize("degrees,hex_str,precise", [
    # (26.444091796875, "12CE", False),
    # (213.90576124191284, "981C5B00", True),
    # (19.171485900878906, "0DA21000", True),
    #(38.044259548187256, "1B0DBFD7", True),
    (89.25868034362793, "3F790D00", True)
])
def test_hex_to_degrees_and_opposite(degrees, hex_str, precise):
    assert hex_to_degrees(hex_str, precise) == degrees
    assert degrees_to_hex(degrees, precise) == hex_str