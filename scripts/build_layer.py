#!/usr/bin/env python3
"""
Builds the Lambda layer zip from src/torguapi/*.py.

The modules go under python/torguapi/, the layout Lambda puts on sys.path for
a Python layer. Every entry gets a fixed timestamp and Unix mode 0644, so the
zip doesn't depend on when or where it was built. infra/main.tf publishes the
result; it decides when to publish from a hash of the sources, not of this zip.

Usage: scripts/build_layer.py [output zip]
"""

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src" / "torguapi"
DEFAULT_OUTPUT = ROOT / "infra" / "build" / "layer_torguapi.zip"

# The earliest timestamp a zip entry can hold
FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100644  # regular file, rw-r--r--


def build_layer(output):
    """Writes the layer zip to output and returns the archived names"""
    output.parent.mkdir(parents=True, exist_ok=True)
    names = []
    with zipfile.ZipFile(output, "w") as zf:
        for path in sorted(SRC_DIR.glob("*.py")):
            info = zipfile.ZipInfo(f"python/torguapi/{path.name}", FIXED_DATE_TIME)
            info.create_system = 3  # Unix, so external_attr holds the mode
            info.external_attr = FILE_MODE << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, path.read_bytes())
            names.append(info.filename)
    return names


def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    names = build_layer(output)
    if not names:
        sys.exit(f"No modules found in {SRC_DIR}")
    for name in names:
        print(f"  {name}")
    print(f"layer -> {output}")


if __name__ == "__main__":
    main()
