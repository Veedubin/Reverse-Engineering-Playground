#!/usr/bin/env python3
"""Append a `## Persona` section to every agent .md file in
.opencode/agents/. Idempotent — skips files that already have it.

Run from the RE_Playground directory:
    python3 -m scripts.append_persona_marker
or:
    python3 .opencode/agents/_append_persona.py
"""

from pathlib import Path
import sys

PERSONA_BLOCK = """

## Persona

<!-- PERSONA-MARKER: DO NOT REMOVE THIS COMMENT.
     Everything below this line is YOUR customizable persona for this agent.
     Everything above is the protocol/tooling/identity and should not be edited.
     Use `boomerang-customize` or edit this section directly.
     The first H2 with the title "Persona" is the one that gets replaced. -->

_Default: General-purpose reverse engineering assistant. Replace this with a
description of the specific work you want this agent to focus on — for example
"Android APK analysis with Frida", "ARM firmware RE on Cortex-M", "network
protocol reversing with Wireshark", or "malware triage and IOC extraction".

Delete this paragraph and write your own below._
"""


def main() -> int:
    agents_dir = Path(__file__).resolve().parent
    modified = 0
    skipped = 0

    for f in sorted(agents_dir.glob("*.md")):
        text = f.read_text()
        if "## Persona" in text:
            skipped += 1
            continue
        if not text.endswith("\n"):
            text += "\n"
        f.write_text(text + PERSONA_BLOCK)
        modified += 1
        print(f"+ {f.name}")

    print(f"\nModified: {modified}   Skipped (already has marker): {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
