#!/usr/bin/env python3
"""Render diagram-like ASCII code fences into PNGs and link them in READMEs.

This complements scripts/gen_diagrams.py: hand-drawn diagrams cover chapter
overview figures, while this script preserves dense timing/layout ASCII figures
as readable PNG assets next to the chapters.
"""
import hashlib
import os
import re
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams["font.family"] = [
    "Noto Sans CJK JP",
    "DejaVu Sans Mono",
]
mpl.rcParams["axes.unicode_minus"] = False

BASE = Path(__file__).resolve().parents[1]
FENCE_RE = re.compile(r"```([^\n]*)\n(.*?)\n```", re.S)
DIAGRAM_CHARS = set("┌┐└┘├┤┬┴┼─│↑↓←→╱╲╳█▁▂▃▄▅▆▇")
KEYWORDS = (
    "CLK", "clk", "CPU", "DMA", "UART", "SPI", "I2C", "CAN", "USB",
    "AXI", "AHB", "APB", "SCK", "SCL", "SDA", "MOSI", "MISO", "SOF",
    "Flash", "Host", "Device", "valid", "ready", "req", "ack",
)


def is_diagram(lang, body):
    if lang.strip():
        return False
    stripped = body.strip("\n")
    if not stripped:
        return False
    lines = stripped.splitlines()
    if len(lines) < 2:
        return False
    char_hits = sum(1 for ch in stripped if ch in DIAGRAM_CHARS)
    arrow_hits = stripped.count("->") + stripped.count("=>") + stripped.count("--")
    keyword_hits = sum(1 for kw in KEYWORDS if kw in stripped)
    return char_hits >= 3 or (arrow_hits >= 2 and keyword_hits >= 1)


def section_title(text, pos):
    title = "ASCII 示意图"
    for line in text[:pos].splitlines():
        if line.startswith("## "):
            title = line.lstrip("# ").strip()
    return title


def image_name(index, title, body):
    digest = hashlib.sha1(body.encode("utf-8")).hexdigest()[:8]
    safe = re.sub(r"[^0-9A-Za-z]+", "_", title).strip("_").lower()
    safe = safe[:36] or "diagram"
    return f"ascii_{index:02d}_{safe}_{digest}.png"


def render_ascii_png(body, title, out_path):
    lines = body.strip("\n").splitlines()
    max_cols = max(len(line) for line in lines)
    width = max(7.5, min(18, max_cols * 0.135 + 1.2))
    height = max(2.6, min(14, len(lines) * 0.33 + 1.5))

    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_facecolor("white")
    ax.axis("off")

    ax.text(
        0.02, 0.95, title,
        transform=ax.transAxes,
        ha="left", va="top",
        fontsize=12, fontweight="bold",
        color="#263238",
    )
    ax.text(
        0.02, 0.86, body.strip("\n"),
        transform=ax.transAxes,
        ha="left", va="top",
        fontsize=10.5,
        family="Noto Sans CJK JP",
        color="#263238",
        linespacing=1.22,
        bbox=dict(
            boxstyle="round,pad=0.55,rounding_size=0.03",
            facecolor="#f8fbff",
            edgecolor="#2f80ed",
            linewidth=1.4,
        ),
    )
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def ensure_chapter_source(chapter_dir):
    src_dir = chapter_dir / "images" / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    source = src_dir / "generate_ascii_diagrams.py"
    source.write_text(
        '''#!/usr/bin/env python3
"""Generate PNGs for this chapter's ASCII diagrams."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.gen_ascii_diagrams import process_readme


if __name__ == "__main__":
    process_readme(ROOT / Path(__file__).resolve().parents[2].name / "README.md")
''',
        encoding="utf-8",
    )


def process_readme(readme):
    chapter_dir = readme.parent
    text = readme.read_text(encoding="utf-8")
    out_dir = chapter_dir / "images" / "ascii"
    out_dir.mkdir(parents=True, exist_ok=True)
    ensure_chapter_source(chapter_dir)

    matches = list(FENCE_RE.finditer(text))
    replacements = []
    diagram_index = 0

    for match in matches:
        lang, body = match.group(1), match.group(2)
        if not is_diagram(lang, body):
            continue
        diagram_index += 1
        title = section_title(text, match.start())
        name = image_name(diagram_index, title, body)
        out_path = out_dir / name
        render_ascii_png(body, title, out_path)

        link = f"\n\n![{title}](images/ascii/{name})"
        after = text[match.end():match.end() + len(link) + 8]
        if f"images/ascii/{name}" not in after:
            replacements.append((match.end(), link))

    if replacements:
        updated = text
        for pos, link in reversed(replacements):
            updated = updated[:pos] + link + updated[pos:]
        readme.write_text(updated, encoding="utf-8")

    return diagram_index


def main():
    total = 0
    for readme in sorted(BASE.glob("*/README.md")):
        count = process_readme(readme)
        if count:
            print(f"{readme.parent.name}: {count}")
            total += count
    print(f"Done. rendered {total} ASCII diagrams.")


if __name__ == "__main__":
    main()
