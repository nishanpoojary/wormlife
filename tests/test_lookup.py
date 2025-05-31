import numpy as np
from src.lookup import build_tables, INVALID


def test_build_tables_no_wormholes_neighbors():
    """
    GIVEN a 3×3 board with no wormholes (horiz={}, vert={})
    WHEN build_tables is called
    THEN each cell should have its orthogonal neighbor indices (if present),
         or INVALID if the neighbor would fall off the grid boundary.
    """
    h, w = 3, 3

    # Call build_tables with empty wormhole dicts
    nbr_r, nbr_c = build_tables(h, w, horiz={}, vert={})

    # Center cell (1,1) should have:
    #   up    → (0,1)
    #   right → (1,2)
    #   down  → (2,1)
    #   left  → (1,0)
    assert nbr_r[1, 1, 0] == 0 and nbr_c[1, 1, 0] == 1  # ↑ neighbor
    assert nbr_r[1, 1, 1] == 1 and nbr_c[1, 1, 1] == 2  # → neighbor
    assert nbr_r[1, 1, 2] == 2 and nbr_c[1, 1, 2] == 1  # ↓ neighbor
    assert nbr_r[1, 1, 3] == 1 and nbr_c[1, 1, 3] == 0  # ← neighbor

    # Corner cell (0,0) has no up or left neighbor → INVALID
    assert nbr_r[0, 0, 0] == INVALID and nbr_c[0, 0, 0] == INVALID  # ↑ invalid
    assert nbr_r[0, 0, 1] == 0 and nbr_c[0, 0, 1] == 1           # → neighbor at (0,1)
    assert nbr_r[0, 0, 2] == 1 and nbr_c[0, 0, 2] == 0           # ↓ neighbor at (1,0)
    assert nbr_r[0, 0, 3] == INVALID and nbr_c[0, 0, 3] == INVALID  # ← invalid


def test_build_tables_with_simple_wormhole_minimal(tmp_path):
    """
    GIVEN a 3×3 board with a single horizontal wormhole mapping (0,1)<->(2,1)
    WHEN build_tables is called with that horiz dict
    THEN it should return two NumPy arrays (nbr_r and nbr_c) of shape (3,3,4),
         with values in [0..2] or INVALID. This is a minimal check to avoid KeyErrors.
    """
    h, w = 3, 3
    horiz = { (0, 1): (2, 1), (2, 1): (0, 1) }
    vert = {}

    # Call build_tables with one horizontal tunnel
    nbr_r, nbr_c = build_tables(h, w, horiz=horiz, vert=vert)

    # Verify the returned objects are NumPy arrays of the correct shape
    assert isinstance(nbr_r, np.ndarray) and isinstance(nbr_c, np.ndarray)
    assert nbr_r.shape == (h, w, 4)
    assert nbr_c.shape == (h, w, 4)

    # Collect the unique values and ensure they lie in [0..h-1] or are INVALID
    unique_r = np.unique(nbr_r)
    unique_c = np.unique(nbr_c)
    valid_r = set(range(h)) | {INVALID}
    valid_c = set(range(w)) | {INVALID}

    assert set(unique_r.tolist()) <= valid_r, "Row neighbors out of valid range"
    assert set(unique_c.tolist()) <= valid_c, "Column neighbors out of valid range"
