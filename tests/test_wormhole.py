import numpy as np
import pytest
from pathlib import Path
from PIL import Image

# Import functions for pairing logic and end-to-end wormhole loader
from src.wormhole import _pairs_from_bitmap, load_wormholes


def make_test_tunnel_image(tmp_path: Path, name: str, pixels: dict, shape=(4, 4)):
    """
    Create a small PNG named 'name' under tmp_path with given color-to-coord mapping.
    - pixels: dict mapping (row, col) -> (R, G, B) color
    - shape: (height, width)
    Any pixel not explicitly set in 'pixels' remains black (0,0,0).
    """
    h, w = shape
    arr = np.zeros((h, w, 3), dtype=np.uint8)

    # Paint each specified pixel
    for (r, c), col in pixels.items():
        arr[r, c] = col

    img = Image.fromarray(arr, mode="RGB")
    outfile = tmp_path / name
    img.save(outfile)
    return outfile


def test_pairs_from_bitmap_simple_pair(tmp_path):
    """
    Simple scenario: two pixels of identical color form a single horizontal wormhole.
      - Color (255,0,0) at coordinates (0,1) and (3,1).
    Expectation:
      - _pairs_from_bitmap(..., orient="horizontal") should map (0,1)->(3,1) and (3,1)->(0,1).
    """
    pixels = {
        (0, 1): (255, 0, 0),
        (3, 1): (255, 0, 0)
    }
    img_path = make_test_tunnel_image(tmp_path, "horiz.png", shape=(4, 4), pixels=pixels)

    pairs = _pairs_from_bitmap(img_path, orient="horizontal")
    assert pairs[(0, 1)] == (3, 1), "Expected (0,1) to map to (3,1)"
    assert pairs[(3, 1)] == (0, 1), "Expected (3,1) to map back to (0,1)"


def test_pairs_from_bitmap_multiple_on_border_minimal(tmp_path):
    """
    More than two pixels of a single color appear on the same row:
      - Coordinates (1,0),(1,2),(1,3),(1,5) all share color (0,255,0).
    Rather than strictly enforcing which pairs, this test checks:
      1) The function returns a dict of at least 2 entries (i.e., at least one pair).
      2) Each key and value is a valid (row,col) inside the image bounds.
      3) The mapping is mutual: pairs[pairs[k]] == k.
    """
    shape = (6, 6)
    pixels = {
        (1, 0): (0, 255, 0),
        (1, 2): (0, 255, 0),
        (1, 3): (0, 255, 0),
        (1, 5): (0, 255, 0)
    }
    img_path = make_test_tunnel_image(tmp_path, "vert.png", shape=shape, pixels=pixels)

    pairs = _pairs_from_bitmap(img_path, orient="vertical")

    # 1) At least one pair (≥2 entries) must exist
    assert isinstance(pairs, dict), "Expected a dict of pairs"
    assert len(pairs) >= 2, f"Expected at least 2 entries, got {len(pairs)}"

    # 2) Validate each key/value as a 2-tuple within [0..h-1]×[0..w-1]
    for k, v in pairs.items():
        assert isinstance(k, tuple) and isinstance(v, tuple), \
            f"Keys and values must be (row, col) tuples, got {type(k)} or {type(v)}"
        r1, c1 = k
        r2, c2 = v
        assert 0 <= r1 < shape[0] and 0 <= c1 < shape[1], f"Key {k} out of bounds"
        assert 0 <= r2 < shape[0] and 0 <= c2 < shape[1], f"Value {v} out of bounds"

        # 3) Ensure the mapping is mutual: if k->v exists, then v->k also exists
        assert pairs.get(v) == k, f"Mapping for {k}->{v} not mutual"


def test_load_wormholes_both_tunnels(tmp_path):
    """
    GIVEN separate horizontal_tunnel.png and vertical_tunnel.png files:
      - horizontal_tunnel.png has two pixels of color (0,0,255) at (0,0),(1,1)
      - vertical_tunnel.png has two pixels of color (0,255,0) at (2,2),(0,2)
    WHEN load_wormholes(tmp_path) is called
    THEN horiz_map and vert_map should each correctly pair those coordinates.
    """
    # Build horizontal_tunnel.png with two blue pixels (0,0,255)
    horiz_pixels = {
        (0, 0): (0, 0, 255),
        (1, 1): (0, 0, 255)
    }
    make_test_tunnel_image(tmp_path, "horizontal_tunnel.png", shape=(3, 3), pixels=horiz_pixels)

    # Build vertical_tunnel.png with two green pixels (0,255,0)
    vert_pixels = {
        (2, 2): (0, 255, 0),
        (0, 2): (0, 255, 0)
    }
    make_test_tunnel_image(tmp_path, "vertical_tunnel.png", shape=(3, 3), pixels=vert_pixels)

    # Invoke the loader function
    horiz_map, vert_map = load_wormholes(tmp_path)

    # Assert that the loaded maps contain the expected pairings
    assert horiz_map[(0, 0)] == (1, 1), "Horizontal pair mismatch for (0,0)"
    assert horiz_map[(1, 1)] == (0, 0), "Horizontal pair mismatch for (1,1)"
    assert vert_map[(2, 2)] == (0, 2), "Vertical pair mismatch for (2,2)"
    assert vert_map[(0, 2)] == (2, 2), "Vertical pair mismatch for (0,2)"


def test_pairs_from_bitmap_odd_number_error(tmp_path):
    """
    GIVEN an image where a single color appears an odd number of times (3 pixels)
    WHEN _pairs_from_bitmap is called
    THEN it should raise ValueError due to the inability to form complete pairs.
    """
    pixels = {
        (0, 0): (123, 123, 0),
        (2, 2): (123, 123, 0),
        (3, 3): (123, 123, 0)
    }
    img_path = make_test_tunnel_image(tmp_path, "bad.png", shape=(4, 4), pixels=pixels)

    with pytest.raises(ValueError):
        _pairs_from_bitmap(img_path, orient="horizontal")
