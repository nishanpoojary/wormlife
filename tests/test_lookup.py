# tests/test_lookup.py
from srcs.lookup import build_tables


def test_lookup_identity_when_no_portals(tmp_path):
    # 3×3 empty tunnel images → no portals
    h, w = 3, 3
    horiz, vert = {}, {}
    nbr_r, nbr_c = build_tables(h, w, horiz, vert)
    # Top of (1,1) should be (0,1), etc.
    assert nbr_r[1, 1, 0] == 0 and nbr_c[1, 1, 0] == 1  # top
    assert nbr_r[1, 1, 1] == 1 and nbr_c[1, 1, 1] == 2  # right
