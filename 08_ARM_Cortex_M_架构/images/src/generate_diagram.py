#!/usr/bin/env python3
"""Generate memory_map.png for this chapter.

This chapter-local entry point keeps the drawing source next to the image while
reusing the shared visual helpers in scripts/gen_diagrams.py.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.gen_diagrams import ch08


if __name__ == "__main__":
    ch08()
