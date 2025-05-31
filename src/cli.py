# src/cli.py

"""
Command-line interface for the Wormhole Game of Life simulator.

Examples
--------
# Run the reference pattern in examples/example-0 (from repo root):
$ python -m wormlife.cli example-0

# Alternatively, specify the full path to the example:
$ python -m wormlife.cli examples/example-1

# Provide custom snapshot generations:
$ python -m wormlife.cli examples/example-0 --milestones 5 15 25
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from .io import load_boolean_board
from .wormhole import load_wormholes
from .lookup import build_tables
from .engine import step

__all__ = ["main"]


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m wormlife.cli",
        description="Run a Wormhole Game of Life simulation and save PNG snapshots."
    )
    parser.add_argument(
        "folder",
        help=(
            "Folder containing 'starting_position.png' and tunnel bitmaps "
            "('horizontal_tunnel.png', 'vertical_tunnel.png')."
        )
    )
    parser.add_argument(
        "--milestones", "-m",
        type=int,
        nargs="+",
        default=[1, 10, 100, 1000],
        metavar="GEN",
        help="Generation numbers for which to write <GEN>.png (default: 1 10 100 1000)."
    )
    return parser.parse_args(argv)


def _resolve_folder(folder: str | Path) -> Path:
    """
    Accept either:
      • a path to an existing directory (e.g. 'examples/example-0'), or
      • just the example name if under 'examples/' (e.g. 'example-0').

    Raises:
        FileNotFoundError if no matching folder is found.
    """
    p = Path(folder)
    if p.is_dir():
        return p

    candidate = Path("examples") / folder
    if candidate.is_dir():
        return candidate

    raise FileNotFoundError(
        f"✗ cannot find example folder '{folder}'. Run with --help for usage."
    )


def _save_png(board: np.ndarray, outfile: Path) -> None:
    """
    Save a boolean board as a black‐and‐white PNG.
      • True → white (255)
      • False → black (0)
    """
    Image.fromarray((board.astype(np.uint8) * 255), mode="L").save(outfile)


def _run_sim(example_dir: Path, milestones: list[int]) -> None:
    """
    Perform the simulation up to max(milestones) and write PNGs at each milestone.

    Parameters
    ----------
    example_dir : Path
        Directory containing starting_position.png, horizontal_tunnel.png, vertical_tunnel.png
    milestones : list[int]
        Generation numbers to dump snapshots (e.g. [1, 10, 100, 1000]).
    """
    board = load_boolean_board(example_dir)
    h, w = board.shape

    horiz, vert = load_wormholes(example_dir)
    nbr_r, nbr_c = build_tables(h, w, horiz, vert)

    current = board.copy()
    last_gen = max(milestones)
    for gen in range(1, last_gen + 1):
        current = step(current, nbr_r, nbr_c)
        if gen in milestones:
            out_path = example_dir / f"{gen}.png"
            _save_png(current, out_path)
            print(f"✓ {out_path}")


def main(argv: list[str] | None = None) -> None:
    ns = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        folder_path = _resolve_folder(ns.folder)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    _run_sim(folder_path, ns.milestones)


if __name__ == "__main__":
    main()
