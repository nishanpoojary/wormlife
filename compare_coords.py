from pathlib import Path
import numpy as np
from PIL import Image

MILESTONES = [1, 10, 100, 1000]
LOG_PATH   = Path("mismatch_log.txt")   # ← destination file

def load(path: Path) -> np.ndarray:
    """Load image → bool array (True = pixel > 127)."""
    return np.asarray(Image.open(path).convert("L")) > 127

# Collect log lines
lines: list[str] = []

for folder in sorted(Path(".").glob("example-*")):
    for g in MILESTONES:
        gen = folder / f"{g}.png"
        exp = folder / f"expected-{g}.png"
        if not gen.exists() or not exp.exists():
            lines.append(f"missing {gen} or {exp}\n")
            continue

        ours, ref = load(gen), load(exp)
        diff = np.argwhere(ours ^ ref)   # coordinates that differ
        if diff.size:
            lines.append(f"\n{folder.name}  gen {g}\n")
            for r, c in diff[:10]:       # first 10 coords for brevity
                lines.append(
                    f"  mismatch at (row={r}, col={c})   "
                    f"ours={int(ours[r,c])}  exp={int(ref[r,c])}\n"
                )
            if diff.shape[0] > 10:
                lines.append(f"  … {diff.shape[0]-10} more pixels differ\n")

# Write (overwriting any existing file)
LOG_PATH.write_text("".join(lines) or "🎉  No mismatches found.\n")
print(f"Log written to {LOG_PATH.resolve()}")
