#!/usr/bin/env python3
"""
scripts/cross-binary-match.py — diff the production binary against upstream.

Compares two ELF binaries (typically `llama-server` or `libllama.so`) and
produces two outputs:

  1. `cross-binary-diff-additions.txt` — symbols in PRODUCTION but not
     in UPSTREAM. These are the highest-priority findings.

  2. `cross-binary-diff-deletions.txt` — symbols in UPSTREAM but not
     in PRODUCTION. These may indicate removed features.

  3. `cross-binary-diff-functions.md` — human-readable Markdown report
     appended to docs/cross-binary-diff.md.

The diff is symbol-based; it does NOT do byte-level comparison. For byte
diff, see the manual procedure in docs/cross-binary-diff.md.

Usage:
    ./scripts/cross-binary-match.py \
        --upstream /tmp/llama.cpp-build/build/bin/libllama.so \
        --production /path/to/production/libllama.so

    # Or with a different Ghidra project path
    ./scripts/cross-binary-match.py \
        --upstream /path/upstream.elf \
        --production /path/production.elf \
        --output-dir /path/to/output/

Stdlib only — no third-party dependencies. Works on Linux, macOS, BSD.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Symbol:
    """A demangled C++ symbol from `nm --defined-only`."""

    name: str  # demangled
    raw_name: str  # mangled
    address: int  # hex
    size: int  # bytes
    section: str  # .text, .rodata, etc.

    @property
    def key(self) -> str:
        # The demangled name is the diff key. Two symbols with the same
        # name but different addresses (because of PIE/ASLR) are
        # considered the same function.
        return self.name

    def __str__(self) -> str:
        return f"0x{self.address:016x} {self.size:8d} {self.section:20s} {self.name}"


# ---------------------------------------------------------------------------
# nm invocation
# ---------------------------------------------------------------------------


def _resolve_nm() -> str:
    """Return the path to `nm` (LLD's `llvm-nm` is also acceptable)."""
    for candidate in ("nm", "llvm-nm", "x86_64-linux-gnu-nm"):
        path = _which(candidate)
        if path:
            return path
    raise RuntimeError(
        "No `nm` binary found. Install binutils (apt install binutils) "
        "or LLVM (brew install llvm)."
    )


def _which(name: str) -> str | None:
    from shutil import which

    return which(name)


def _demangle(nm: str, raw: str) -> str:
    """Use nm's -C flag for demangling; we never call c++filt directly."""
    # The C++ filter is done by `nm -C` below. raw_name in this dataclass
    # stores the mangled form; name stores the demangled form.
    return raw  # caller has already demangled.


def parse_nm(binary: Path, *, nm: str | None = None) -> List[Symbol]:
    """Run `nm -D --defined-only -C` on a binary and parse the output.

    We use `-D` (dynamic symbols) so we get the exported C/C++ API plus
    internal text symbols (the binary is not stripped so the static
    table is also useful, but `-D` is more portable across build
    configurations).
    """
    nm = nm or _resolve_nm()
    # We use the ELF symbol table, not just dynamic. Pass --no-demangle
    # then demangle each line with c++filt to keep the mangled name
    # available for byte-level diff (function hash, etc.).
    cmd = [nm, "--defined-only", "-P", str(binary)]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    out: List[Symbol] = []
    for line in proc.stdout.splitlines():
        # nm -P format: name type value size
        #   name  type  value  size
        # where size may be empty for ABS / UNDEF symbols.
        parts = line.strip().split()
        if len(parts) < 3:
            continue
        name, symtype, value = parts[0], parts[1], parts[2]
        size = int(parts[3], 16) if len(parts) >= 4 and parts[3] else 0
        if symtype not in ("T", "W", "R", "D", "B"):  # text/weak/rodata/data/bss
            continue
        try:
            address = int(value, 16)
        except ValueError:
            continue
        # Demangle: nm -P doesn't do it. Use c++filt.
        demangled = _cxxfilt(name) if name.startswith("_Z") else name
        section = _section_for_type(symtype)
        out.append(
            Symbol(
                name=demangled,
                raw_name=name,
                address=address,
                size=size,
                section=section,
            )
        )
    return out


def _section_for_type(symtype: str) -> str:
    return {
        "T": ".text",
        "W": ".text (weak)",
        "R": ".rodata",
        "D": ".data",
        "B": ".bss",
    }.get(symtype, "??")


def _cxxfilt(mangled: str) -> str:
    """Demangle a C++ symbol using `c++filt`. Pass-through on failure."""
    for cand in ("c++filt", "llvm-cxxfilt", "x86_64-linux-gnu-c++filt"):
        path = _which(cand)
        if not path:
            continue
        try:
            proc = subprocess.run(
                [path],
                input=mangled,
                capture_output=True,
                text=True,
                check=True,
            )
            return proc.stdout.strip() or mangled
        except subprocess.CalledProcessError:
            continue
    return mangled


# ---------------------------------------------------------------------------
# Diff
# ---------------------------------------------------------------------------


def diff_symbols(
    upstream: List[Symbol],
    production: List[Symbol],
) -> Tuple[List[Symbol], List[Symbol], List[Tuple[Symbol, Symbol]]]:
    """Compute (additions, deletions, same-name-different-size).

    - additions: in production, not in upstream (by name)
    - deletions: in upstream, not in production (by name)
    - same-name-different-size: in both but with different size (suspicious)
    """
    upstream_by_name: Dict[str, Symbol] = {s.name: s for s in upstream}
    production_by_name: Dict[str, Symbol] = {s.name: s for s in production}

    additions = [s for s in production if s.name not in upstream_by_name]
    deletions = [s for s in upstream if s.name not in production_by_name]

    size_changed: List[Tuple[Symbol, Symbol]] = []
    for name, prod_sym in production_by_name.items():
        if name in upstream_by_name:
            up_sym = upstream_by_name[name]
            if up_sym.size != prod_sym.size and up_sym.size > 0 and prod_sym.size > 0:
                size_changed.append((up_sym, prod_sym))

    return additions, deletions, size_changed


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

# Keywords that, when found in an addition's name, are high-priority findings.
HIGH_PRIORITY_KEYWORDS = [
    "filter",
    "censor",
    "block",
    "deny",
    "policy",
    "harmful",
    "content",
    "refuse",
    "sanitize",
    "blacklist",
    "whitelist",
    "telemetry",
    "phone_home",
    "phone-home",
    "validate_output",
    "rewrite",
    "inject",
    "prompt_guard",
    "prompt-guard",
    "safety_check",
    "safety-check",
    "alignment",
    "jailbreak",
    "redact",
    "obfuscat",
    "encode",
    "encrypt",
]

# Stdlib prefixes that are NOT meaningful differences.
STDLIB_PREFIXES = (
    "std::",
    "__cxx",
    "__gnu_cxx",
    "_ZNSt",
    "_ZSt",
    "_ZNKSt",
    "_ZNKSs",
    "_ZNKSb",
    "_ZNSs",
    "_ZNSb",
    "_ZNSa",
    "_M_",
    "operator new",
    "operator delete",
    "vtable for __cxxabiv1",
    "typeinfo for __cxxabiv1",
    "__stack_chk",
    "frame_dummy",
    "__do_global",
    "operator+",
    "operator-",
    "operator*",
    "operator/",
    "operator<<",
    "operator>>",
    "operator==",
    "operator!=",
    "non-virtual thunk to",
    "virtual thunk to",
    "guard variable for",
    "VTT for",
    "_GLOBAL__sub_I_",
    "typeinfo name for",
)


def _is_meaningful(symbol: Symbol) -> bool:
    name = symbol.name
    if not name or name.startswith("__"):
        return True  # compiler-rt symbols are interesting
    for prefix in STDLIB_PREFIXES:
        if name.startswith(prefix):
            return False
    return True


def _is_high_priority(symbol: Symbol) -> bool:
    name_lc = symbol.name.lower()
    return any(kw in name_lc for kw in HIGH_PRIORITY_KEYWORDS)


def render_report(
    additions: List[Symbol],
    deletions: List[Symbol],
    size_changed: List[Tuple[Symbol, Symbol]],
    upstream_path: Path,
    production_path: Path,
) -> str:
    lines: List[str] = []
    lines.append("# Cross-Binary Diff Report")
    lines.append("")
    lines.append(f"- **Upstream**: `{upstream_path}`")
    lines.append(f"- **Production**: `{production_path}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    meaningful_additions = [s for s in additions if _is_meaningful(s)]
    meaningful_deletions = [s for s in deletions if _is_meaningful(s)]
    lines.append(
        f"- **Total additions** (symbols in production, not in upstream): "
        f"{len(additions)} ({len(meaningful_additions)} non-stdlib)"
    )
    lines.append(
        f"- **Total deletions** (symbols in upstream, not in production): "
        f"{len(deletions)} ({len(meaningful_deletions)} non-stdlib)"
    )
    lines.append(f"- **Size changes** (same name, different size): {len(size_changed)}")
    high_pri = [s for s in meaningful_additions if _is_high_priority(s)]
    if high_pri:
        lines.append("")
        lines.append("## ⚠️ High-priority findings")
        lines.append("")
        lines.append(
            "These additions match keywords commonly used by backdoors, "
            "content filters, telemetry, and prompt-injection guards. "
            "Investigate each."
        )
        lines.append("")
        for s in sorted(high_pri, key=lambda x: x.name):
            lines.append(f"- `{s.name}` ({s.size} bytes) at `0x{s.address:x}`")
    lines.append("")
    lines.append("## Additions (in production, not in upstream) — non-stdlib")
    lines.append("")
    if meaningful_additions:
        lines.append("| Size | Address | Symbol |")
        lines.append("|---:|---:|---|")
        for s in sorted(meaningful_additions, key=lambda x: -x.size):
            lines.append(f"| {s.size} | `0x{s.address:x}` | `{s.name}` |")
    else:
        lines.append(
            "_None — the production binary's symbol set is a subset of upstream._"
        )
    lines.append("")
    lines.append("## Deletions (in upstream, not in production) — non-stdlib")
    lines.append("")
    if meaningful_deletions:
        lines.append("| Size | Address | Symbol |")
        lines.append("|---:|---:|---|")
        for s in sorted(meaningful_deletions, key=lambda x: -x.size):
            lines.append(f"| {s.size} | `0x{s.address:x}` | `{s.name}` |")
    else:
        lines.append("_None — the production binary includes all upstream symbols._")
    lines.append("")
    lines.append("## Size changes (same name, different size)")
    lines.append("")
    if size_changed:
        lines.append("| Upstream size | Production size | Δ | Symbol |")
        lines.append("|---:|---:|---:|---|")
        for up_sym, prod_sym in sorted(
            size_changed, key=lambda p: -abs(p[1].size - p[0].size)
        ):
            delta = prod_sym.size - up_sym.size
            lines.append(
                f"| {up_sym.size} | {prod_sym.size} | {delta:+d} | `{up_sym.name}` |"
            )
    else:
        lines.append("_None._")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(
        description="Diff two ELF binaries (production vs upstream) by symbol set.",
    )
    p.add_argument(
        "--upstream",
        required=True,
        type=Path,
        help="Path to the upstream binary (built from the pinned commit).",
    )
    p.add_argument(
        "--production",
        required=True,
        type=Path,
        help="Path to the production binary to audit.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs"),
        help="Directory to write report files into (default: docs/).",
    )
    args = p.parse_args(argv)

    for label, path in (("upstream", args.upstream), ("production", args.production)):
        if not path.exists():
            print(f"error: {label} binary not found: {path}", file=sys.stderr)
            return 2

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[cross-binary-match] upstream:  {args.upstream}")
    print(f"[cross-binary-match] production: {args.production}")
    print(f"[cross-binary-match] output:     {output_dir}/")

    print("[cross-binary-match] parsing upstream symbols...")
    upstream = parse_nm(args.upstream)
    print(f"[cross-binary-match]   {len(upstream)} symbols")

    print("[cross-binary-match] parsing production symbols...")
    production = parse_nm(args.production)
    print(f"[cross-binary-match]   {len(production)} symbols")

    additions, deletions, size_changed = diff_symbols(upstream, production)

    print(
        f"[cross-binary-match] diff: {len(additions)} additions, "
        f"{len(deletions)} deletions, {len(size_changed)} size changes"
    )

    report = render_report(
        additions,
        deletions,
        size_changed,
        args.upstream,
        args.production,
    )

    md_path = output_dir / "cross-binary-diff-functions.md"
    md_path.write_text(report)
    print(f"[cross-binary-match] wrote {md_path}")

    # Also write the raw additions / deletions lists as text files
    (output_dir / "cross-binary-diff-additions.txt").write_text(
        "\n".join(str(s) for s in sorted(additions, key=lambda x: x.name)) + "\n",
    )
    (output_dir / "cross-binary-diff-deletions.txt").write_text(
        "\n".join(str(s) for s in sorted(deletions, key=lambda x: x.name)) + "\n",
    )
    print(f"[cross-binary-match] wrote {output_dir}/cross-binary-diff-additions.txt")
    print(f"[cross-binary-match] wrote {output_dir}/cross-binary-diff-deletions.txt")

    # High-priority summary to stdout
    meaningful = [s for s in additions if _is_meaningful(s)]
    high_pri = [s for s in meaningful if _is_high_priority(s)]
    if high_pri:
        print("")
        print("=" * 60)
        print(f"⚠️  HIGH-PRIORITY ADDITIONS: {len(high_pri)}")
        print("=" * 60)
        for s in sorted(high_pri, key=lambda x: -x.size):
            print(f"  {s.size:8d}  {s.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
