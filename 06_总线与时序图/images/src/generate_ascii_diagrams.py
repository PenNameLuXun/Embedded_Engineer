#!/usr/bin/env python3
"""Generate PNGs for this chapter's ASCII diagrams."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.gen_ascii_diagrams import process_readme


if __name__ == "__main__":
    process_readme(ROOT / Path(__file__).resolve().parents[2].name / "README.md")
