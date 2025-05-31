# Game of Life with Wormholes

A variant of Conway’s Game of Life where cells can “wrap” through colored tunnels (wormholes) to connect distant positions.

## Features

* Loads three PNGs from an input folder:

  * `starting_position.png` (white = alive, other = dead)
  * `horizontal_tunnel.png` (maps pairs of same-colored pixels horizontally)
  * `vertical_tunnel.png` (maps pairs of same-colored pixels vertically)
* Builds neighbor lookup tables that incorporate wormhole teleports.
* Applies standard Game of Life rules (birth, survival, death) on each generation.
* Saves milestone snapshots (e.g. `1.png`, `10.png`, `100.png`, `1000.png`) under the same folder.

## Requirements

* Python 3.8+
* Pillow
* NumPy
* (Dev/testing) pytest

All dependencies are listed in `requirements.txt`.

## Installation

1. Clone or unzip the project so you have the top-level folders:

   ```
   LICENSE
   README.md
   requirements.txt
   src/
   tests/
   examples/
   problems/
   ```
2. (Optional) Create a virtual environment:

   ```
   python3 -m venv .venv
   source .venv/bin/activate      # macOS/Linux
   .venv\Scripts\activate.bat     # Windows PowerShell
   ```
3. Install runtime dependencies:

   ```
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Project Structure

```
.
├── README.md
├── requirements.txt
├── src/
│   ├── cli.py            # CLI entry point
│   ├── engine.py         # Game logic (step)
│   ├── io.py             # Load starting_position → boolean array
│   ├── loader_check.py   # Verify existence/size/mode of PNGs
│   ├── lookup.py         # Build neighbor tables with wormholes
│   └── wormhole.py       # Parse tunnel PNGs → coordinate pairs
├── tests/
│   ├── test_cli.py
│   ├── test_engine.py
│   ├── test_io.py
│   ├── test_loader_check.py
│   ├── test_lookup.py
│   ├── test_wormhole.py
│   └── test_wormhole_io_integration.py
├── examples/
│   ├── example-0/
│   │   ├── starting_position.png
│   │   ├── horizontal_tunnel.png
│   │   ├── vertical_tunnel.png
│   │   ├── 1.png
│   │   ├── 10.png
│   │   ├── 100.png
│   │   └── 1000.png
│   ├── example-1/
│   ├── example-2/
│   ├── example-3/
│   └── example-4/
└── problems/
    ├── problem-1/
    ├── problem-2/
    ├── problem-3/
    └── problem-4/
```

## How It Works

1. **Load Input Images**

   * `io.load_boolean_board(dir_path)`: loads `starting_position.png` → boolean array `(H,W)`.
   * `wormhole.load_wormholes(dir_path)`: parses `horizontal_tunnel.png` and `vertical_tunnel.png` → two maps of coordinate pairs.

2. **Build Neighbor Lookup**

   * `lookup.build_tables(H, W, horiz_map, vert_map)` → two arrays `(H, W, 4)`: neighbor row/col indices for directions Up/Right/Down/Left, possibly teleporting via wormholes.

3. **Game Logic**

   * `engine.step(board, nbr_r, nbr_c)` → new boolean array after one generation.
   * Counts eight neighbors by first moving orthogonally (using `nbr_r`, `nbr_c`), then moving diagonally (two successive orthogonal hops, respecting wormholes).
   * Applies standard rules:

     * Alive → survives if 2 or 3 neighbors remain alive.
     * Dead → becomes alive if exactly 3 neighbors alive.

4. **CLI Execution**

   * `cli._resolve_folder(input_str)`: accept folder path or `examples/example-N` alias.
   * `cli._run_sim(folder, milestones)`:

     1. Load board + wormholes
     2. Build lookup tables
     3. Repeatedly call `engine.step(...)` until each milestone
     4. Save milestone boards (`{milestone}.png`) using `_save_png()`

## Usage

```bash
# Run default milestones [1,10,100,1000] on example-0
python -m src.cli examples/example-0

# Run custom milestones on a specific folder path
python -m src.cli /path/to/my_input_folder --milestones 5 20 50
```

To verify input files:

```bash
python -m src.loader_check examples/example-0
```

## Running Tests

```bash
pytest -q
```

All unit and integration tests under `tests/` will execute.