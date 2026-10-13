import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "analyses", ROOT / "pipeline", ROOT / "scripts"):
    sys.path.insert(0, str(p))
