# # srcs/wormhole.py
# """
# Utilities to parse wormhole PNGs and build neighbour-lookup tables.

# A colour ≠ black (0,0,0) means “this pixel is a tunnel end”.
# Each colour appears **exactly twice** (PDF spec) :contentReference[oaicite:0]{index=0}.
# """

# from pathlib import Path
# from typing import Dict, List, Tuple

# import numpy as np
# from PIL import Image

# Coord = Tuple[int, int]  # (row, col)
# PairMap = Dict[Coord, Coord]


# def _pairs_from_bitmap(path: Path, orientation: str) -> PairMap:
#     """
#     Build {endpoint_a: endpoint_b, endpoint_b: endpoint_a} for every colour.

#     orientation = "horizontal"  -> endpoints chosen by min/max COL (same row)
#                  = "vertical"    -> endpoints chosen by min/max ROW (same col)
#     """
#     assert orientation in {"horizontal", "vertical"}
#     img = Image.open(path).convert("RGB")
#     arr = np.asarray(img)  # (H, W, 3)
#     h, w, _ = arr.shape

#     colour_to_coords: Dict[Tuple[int, int, int], List[Coord]] = {}
#     for r in range(h):
#         for c in range(w):
#             colour = tuple(arr[r, c])
#             if colour == (0, 0, 0):  # background
#                 continue
#             colour_to_coords.setdefault(colour, []).append((r, c))

#     pairs: PairMap = {}
#     for colour, coords in colour_to_coords.items():
#         # Pick extreme points depending on orientation
#         if orientation == "horizontal":
#             # All coords should share the same row; pick leftmost & rightmost
#             left = min(coords, key=lambda t: t[1])
#             right = max(coords, key=lambda t: t[1])
#             a, b = left, right
#         else:  # vertical
#             # All coords share same col; pick topmost & bottommost
#             top = min(coords, key=lambda t: t[0])
#             bottom = max(coords, key=lambda t: t[0])
#             a, b = top, bottom

#         pairs[a] = b
#         pairs[b] = a

#     return pairs


# def load_wormholes(example_dir: str) -> Tuple[PairMap, PairMap]:
#     p = Path(example_dir)
#     horiz = _pairs_from_bitmap(p / "horizontal_tunnel.png", "horizontal")
#     vert = _pairs_from_bitmap(p / "vertical_tunnel.png", "vertical")
#     return horiz, vert

# """
# srcs/wormhole.py  –  Build horizontal / vertical portal maps.

# Works for:
#   • 2-pixel portals
#   • even-length border lines
#   • interior lines / zig-zags (any even length)

# Exports
# -------
# load_wormholes(example_dir) -> (horiz_pairs, vert_pairs)
#   horiz_pairs / vert_pairs : dict[(r, c), (r, c)]
# """

# from __future__ import annotations

# from pathlib import Path
# from typing import Dict, List, Tuple

# import numpy as np
# from PIL import Image

# Coord   = Tuple[int, int]
# PairMap = Dict[Coord, Coord]


# # -----------------------------------------------------------------------------
# # Helpers
# # -----------------------------------------------------------------------------
# def _sequential_pairs(coords: List[Coord]) -> PairMap:
#     """Pair coords 0-1, 2-3, …  (guaranteed even)."""
#     out: PairMap = {}
#     for a, b in zip(coords[0::2], coords[1::2]):
#         out[a] = b
#         out[b] = a
#     return out


# def _pairs_from_bitmap(path: Path, orientation: str) -> PairMap:
#     """
#     Convert one tunnel bitmap to {entrance: exit, …}.

#     orientation = "horizontal" → slice by column order
#                 = "vertical"   → slice by row order
#     """
#     arr = np.asarray(Image.open(path).convert("RGB"))
#     H, W, _ = arr.shape
#     colour_to_coords: Dict[Tuple[int, int, int], List[Coord]] = {}

#     for r in range(H):
#         for c in range(W):
#             colour = tuple(arr[r, c])
#             if colour == (0, 0, 0):      # black → background
#                 continue
#             colour_to_coords.setdefault(colour, []).append((r, c))

#     pairs: PairMap = {}

#     for colour, coords in colour_to_coords.items():
#         n = len(coords)
#         if n % 2 != 0:
#             raise ValueError(
#                 f"{path.name}: colour {colour} appears {n} times (must be even)."
#             )

#         # Order coords along the tunnel direction, then pair sequentially.
#         if orientation == "horizontal":
#             coords.sort(key=lambda rc: (rc[0], rc[1]))   # row, then col
#         else:  # vertical
#             coords.sort(key=lambda rc: (rc[1], rc[0]))   # col, then row

#         pairs.update(_sequential_pairs(coords))

#     return pairs


# # -----------------------------------------------------------------------------
# # Public API
# # -----------------------------------------------------------------------------
# def load_wormholes(example_dir: str | Path) -> Tuple[PairMap, PairMap]:
#     p = Path(example_dir)
#     horiz = _pairs_from_bitmap(p / "horizontal_tunnel.png", "horizontal")
#     vert  = _pairs_from_bitmap(p / "vertical_tunnel.png",   "vertical")
#     return horiz, vert


"""
srcs/wormhole.py
Build horizontal / vertical portal maps exactly as the PDF describes.

Rules
-----
* A colour may appear just twice  → simple two-pixel portal.
* A colour may appear many times along the border:
    - vertical tunnel: coloured pixels on LEFT & RIGHT edges
    - horizontal tunnel: coloured pixels on TOP & BOTTOM edges
  In that case each row/column teleports straight across the board
  (leftmost ⟷ rightmost, topmost ⟷ bottommost) for that row / column.
* Every colour must occur an even number of times; odd → ValueError.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

Coord   = Tuple[int, int]              # (row, col)
PairMap = Dict[Coord, Coord]           # endpoint → partner


# ---------------------------------------------------------------------------
def _pair_extremes(coords: List[Coord],
                   by_row: bool) -> PairMap:
    """Pair leftmost↔rightmost in each row  OR  topmost↔bottommost in each col."""
    bucket: Dict[int, List[int]] = {}
    for r, c in coords:
        key = r if by_row else c
        val = c if by_row else r
        bucket.setdefault(key, []).append(val)

    pairs: PairMap = {}
    for key, vals in bucket.items():
        if len(vals) < 2:
            continue
        a = min(vals)
        b = max(vals)
        if by_row:
            pairs[(key, a)] = (key, b)
            pairs[(key, b)] = (key, a)
        else:
            pairs[(a, key)] = (b, key)
            pairs[(b, key)] = (a, key)
    return pairs


def _pairs_from_bitmap(path: Path, orient: str) -> PairMap:
    """
    Read one tunnel bitmap  →  PairMap for that orientation.

    orient = "vertical"   (connect LEFT edge to RIGHT edge)
           = "horizontal" (connect TOP edge to BOTTOM edge)
    """
    arr = np.asarray(Image.open(path).convert("RGB"))
    H, W, _ = arr.shape

    colour2coords: Dict[Tuple[int, int, int], List[Coord]] = {}
    for r in range(H):
        for c in range(W):
            colour = tuple(arr[r, c])
            if colour == (0, 0, 0):
                continue
            colour2coords.setdefault(colour, []).append((r, c))

    pairs: PairMap = {}
    for colour, coords in colour2coords.items():
        n = len(coords)
        if n % 2:
            raise ValueError(f"{path.name}: colour {colour} appears {n} times (odd)")

        # simple two-pixel portal
        if n == 2:
            a, b = coords
            pairs[a] = b
            pairs[b] = a
            continue

        # border-line tunnel
        if orient == "vertical":
            # pair leftmost↔rightmost pixel in each row
            pairs.update(_pair_extremes(coords, by_row=True))
        elif orient == "horizontal":
            # pair topmost↔bottommost pixel in each column
            pairs.update(_pair_extremes(coords, by_row=False))
        else:  # should not happen
            raise ValueError(f"Unknown orientation {orient!r}")

    return pairs


# ---------------------------------------------------------------------------
def load_wormholes(example_dir: str | Path) -> Tuple[PairMap, PairMap]:
    p = Path(example_dir)
    horiz = _pairs_from_bitmap(p / "horizontal_tunnel.png", "horizontal")
    vert  = _pairs_from_bitmap(p / "vertical_tunnel.png",   "vertical")
    return horiz, vert
