# tests/test_run_smoke.py
import shutil, pathlib, os
from srcs.run_sim import main as run_sim

def test_runner_produces_outputs(tmp_path):
    # Copy a tiny dataset to a temp folder so we don't overwrite originals
    src = pathlib.Path("example-0")
    dst = tmp_path / "case"
    shutil.copytree(src, dst)
    run_sim(str(dst))
    for milestone in [1, 10, 100, 1000]:
        assert (dst / f"{milestone}.png").exists()
