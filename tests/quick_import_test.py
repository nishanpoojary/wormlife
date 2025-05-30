"""
Quick sanity-check: can Python import srcs.wormhole when run from project root?
Run once with `python tests/quick_import_test.py`.
"""
import sys, pathlib, importlib, pprint

# Put project root (parent of 'tests') onto sys.path FIRST
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

print("Project root = ", ROOT)
print("sys.path[0] =", sys.path[0])

try:
    mod = importlib.import_module("srcs.wormhole")
    print("✅  Imported", mod.__name__)
    print("   Location:", pathlib.Path(mod.__file__).relative_to(ROOT))
except ModuleNotFoundError as e:
    print("❌  Import failed:", e)
