# tests/test_wormhole.py
from pathlib import Path
import pytest
from srcs.wormhole import load_wormholes

EXAMPLES = [p for p in Path(".").glob("example-*")]

@pytest.mark.parametrize("folder", EXAMPLES)
def test_wormhole_pairs_are_valid(folder: Path):
    """
    The parser should:
      • return without error
      • map each endpoint to exactly one partner (i.e. dict is symmetric)
    A dataset may legitimately contain zero wormholes.
    """
    horiz, vert = load_wormholes(folder)

    # Every key should map to a partner that maps back to the key
    for a, b in horiz.items():
        assert horiz[b] == a, f"Asymmetry in horizontal mapping {folder}"
    for a, b in vert.items():
        assert vert[b] == a, f"Asymmetry in vertical mapping {folder}"
