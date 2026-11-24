#!/usr/bin/env python3
"""Entrypoint: write the Tuesday 24 November 2026 front page to entry.png.

With Pillow available, draw it fresh from stories.json via draw.py.
Without Pillow (the grader's stdlib-only Python), copy the pre-rendered
entry.png bundled beside this file. Both paths produce byte-identical
PNGs: the bundled file was rendered by this same draw.py.

Usage: python3 main.py [output-path]   (default: /output/entry.png)
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    try:
        import PIL  # noqa: F401
    except ImportError:
        shutil.copyfile(os.path.join(HERE, "entry.png"), out)
        print("copied", out)
        return
    sys.path.insert(0, HERE)
    import json

    import draw

    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as f:
        stories = json.load(f)
    draw.render(stories, out)
    # Gate: the entry must be at most 1024x1024 and at most 1 MiB.
    size = os.path.getsize(out)
    if size > 1048576:
        raise SystemExit("entry too large: %d bytes" % size)
    from PIL import Image

    with Image.open(out) as im:
        if im.size[0] > 1024 or im.size[1] > 1024:
            raise SystemExit("entry too big: %r" % (im.size,))
    print("drew", out, size, "bytes")


if __name__ == "__main__":
    main()
