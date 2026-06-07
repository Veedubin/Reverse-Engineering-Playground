#!/usr/bin/env python3
"""
RE_Playground installer.

Cross-distro tool installer for the Reverse Engineering Playground.
Supports:
  - Arch Linux / CachyOS (pacman + AUR via paru)
  - Ubuntu / Debian (apt + pip)
  - macOS (Homebrew + pip)

Usage:
  ./install.py            Interactive TUI (checkbox list, all checked by default)
  ./install.py --yes      Non-interactive, install everything available
  ./install.py --check    Dry-run: detect OS + report which tools are already installed
  ./install.py --list     Print the tool catalog and exit
  ./install.py --help     Show usage

No vendor binaries are shipped — this script pulls everything from your
distro's package manager, Homebrew, pip, or npm. Tools with no package
available on your platform are marked "manual" and skipped; see README.md.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Callable

# --- Output helpers ---------------------------------------------------------

GREEN = "\033[1;32m"
RED = "\033[1;31m"
YELLOW = "\033[1;33m"
CYAN = "\033[1;36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def color(text: str, c: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{c}{text}{RESET}"


def info(msg: str) -> None:
    print(f"{color('[*]', CYAN)} {msg}")


def ok(msg: str) -> None:
    print(f"{color('[+]', GREEN)} {msg}")


def warn(msg: str) -> None:
    print(f"{color('[!]', YELLOW)} {msg}")


def err(msg: str) -> None:
    print(f"{color('[-]', RED)} {msg}", file=sys.stderr)


def header(msg: str) -> None:
    print()
    print(color("=" * 70, BOLD))
    print(color(f"  {msg}", BOLD))
    print(color("=" * 70, BOLD))


# --- OS / package manager detection ----------------------------------------


@dataclass
class Distro:
    name: str
    family: str  # "arch", "debian", "darwin"
    pm: str  # "pacman", "apt", "brew"
    aur_helper: str | None = None  # "paru" or "yay" (arch only)
    sudo_cmd: str = "sudo"


def detect_distro() -> Distro | None:
    system = platform.system().lower()

    # macOS first — simple
    if system == "darwin":
        if shutil.which("brew"):
            return Distro(name="macOS", family="darwin", pm="brew", sudo_cmd="")
        warn("Homebrew not found. Install it from https://brew.sh first.")
        return None

    # Read /etc/os-release for Linux
    os_release = _read_os_release()
    distro_id = (os_release.get("ID") or "").lower()
    distro_like = (os_release.get("ID_LIKE") or "").lower()

    is_arch_family = (
        distro_id in ("arch", "cachyos", "manjaro", "endeavouros")
        or "arch" in distro_like
    )
    is_debian_family = distro_id in (
        "ubuntu",
        "debian",
        "linuxmint",
        "pop",
        "elementary",
        "zorin",
        "kali",
    ) or any(x in distro_like for x in ("debian", "ubuntu"))

    if is_arch_family and shutil.which("pacman"):
        aur = None
        for helper in ("paru", "yay"):
            if shutil.which(helper):
                aur = helper
                break
        if aur is None:
            warn("No AUR helper found (paru/yay). AUR packages will be skipped.")
        return Distro(
            name=os_release.get("PRETTY_NAME", "Arch Linux"),
            family="arch",
            pm="pacman",
            aur_helper=aur,
        )

    if is_debian_family and shutil.which("apt"):
        return Distro(
            name=os_release.get("PRETTY_NAME", "Debian/Ubuntu"),
            family="debian",
            pm="apt",
        )

    err(f"Unsupported distro: {distro_id!r} (ID_LIKE={distro_like!r})")
    err("Supported: Arch/CachyOS (pacman+paru), Ubuntu/Debian (apt), macOS (brew).")
    return None


def _read_os_release() -> dict[str, str]:
    data: dict[str, str] = {}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    data[k] = v.strip('"').strip("'")
    except FileNotFoundError:
        pass
    return data


# --- Tool catalog -----------------------------------------------------------


@dataclass
class Tool:
    key: str
    name: str
    group: str
    description: str
    bin: str  # binary used to detect installation
    # Install function for this distro family; raises on failure.
    # Returns a short status string ("installed", "skipped", etc.)
    installers: dict[str, Callable[["Tool"], str]] = field(default_factory=dict)
    # If True, the TUI will leave this tool UNCHECKED by default.
    # Use for tools with licensing concerns (GPL), heavy install footprints
    # (angr, semgrep), or limited additional value beyond what's already
    # provided by other tools in the catalog. Users can still opt in
    # manually.
    opt_in: bool = False

    def is_installed(self) -> bool:
        return shutil.which(self.bin) is not None


# --- Install action builders -----------------------------------------------


def _run(
    cmd: list[str], sudo: str = "", env: dict | None = None
) -> subprocess.CompletedProcess:
    full = ([sudo] if sudo else []) + cmd
    return subprocess.run(full, check=False, capture_output=True, text=True, env=env)


def _pacman_install(tool: Tool, as_root: bool) -> str:
    sudo = "sudo" if as_root else ""
    r = _run(["pacman", "-S", "--noconfirm", "--needed", tool.bin], sudo=sudo)
    if r.returncode == 0:
        return "installed"
    return f"failed: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown'}"


def _aur_install(tool: Tool, helper: str, as_root: bool) -> str:
    # AUR helpers must run as a non-root user. We assume the user can sudo
    # without password OR is already non-root.
    if as_root and os.geteuid() == 0:
        return "skipped (run as non-root for AUR)"
    r = _run([helper, "-S", "--noconfirm", "--needed", tool.bin])
    if r.returncode == 0:
        return "installed"
    return f"failed: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown'}"


def _apt_install(tool: Tool, as_root: bool) -> str:
    sudo = "sudo" if as_root else ""
    r = _run(["apt-get", "install", "-y", tool.bin], sudo=sudo)
    if r.returncode == 0:
        return "installed"
    # apt may fail because the package doesn't exist; try a sanity check
    r2 = _run(["apt-cache", "show", tool.bin])
    if r2.returncode != 0:
        return f"manual (no apt package '{tool.bin}')"
    return f"failed: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown'}"


def _pip_install(tool: Tool) -> str:
    r = _run([sys.executable, "-m", "pip", "install", "--user", tool.bin])
    if r.returncode == 0:
        return "installed"
    return f"failed: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown'}"


def _npm_install(tool: Tool) -> str:
    r = _run(["npm", "install", "-g", tool.bin])
    if r.returncode == 0:
        return "installed"
    return f"failed: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown'}"


def _uv_tool_install(tool: Tool, pkg: str | None = None) -> str:
    """Install a Python CLI tool as an isolated `uv tool` (PEP 668 compliant)."""
    name = pkg or tool.bin
    r = _run(["uv", "tool", "install", name])
    if r.returncode == 0:
        return "installed"
    return f"failed: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown'}"


def _pipx_or_pip_install(pkg: str) -> str:
    """Install a Python library — prefer pipx for CLI tools, fall back to pip --user."""
    if shutil.which("pipx"):
        r = _run(["pipx", "install", pkg])
        if r.returncode == 0:
            return "installed"
    r = _run([sys.executable, "-m", "pip", "install", "--user", pkg])
    if r.returncode == 0:
        return "installed"
    return f"failed: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown'}"


def _git_pip_install(repo: str, extras: str = "", pkg_name: str | None = None) -> str:
    """Clone a git repo and `pip install` from source. Use for tools not on PyPI.

    Example: _git_pip_install("https://github.com/foo/bar.git", extras="[full]")
    """
    import tempfile

    target = pkg_name or repo.rstrip("/").split("/")[-1].replace(".git", "")
    with tempfile.TemporaryDirectory() as tmp:
        clone = _run(["git", "clone", "--depth", "1", repo, f"{tmp}/{target}"])
        if clone.returncode != 0:
            return f"failed: git clone: {clone.stderr.strip().splitlines()[-1] if clone.stderr else 'unknown'}"
        spec = f".{extras}" if extras else "."
        r = _run(
            [sys.executable, "-m", "pip", "install", "--user", spec],
            cwd=f"{tmp}/{target}",
        )
        if r.returncode == 0:
            return "installed"
        return f"failed: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown'}"


def _dotnet_tool_install(pkg: str) -> str:
    """Install a .NET global tool (needs dotnet-sdk already on PATH)."""
    if not shutil.which("dotnet"):
        return "skipped (dotnet-sdk not installed)"
    # Ensure ~/.dotnet/tools is on PATH for the current run; persistent PATH
    # modification is left to the user's shell rc (documented in README).
    r = _run(["dotnet", "tool", "install", "-g", pkg])
    if r.returncode == 0:
        return "installed"
    # If the tool is already installed, dotnet tool install fails — that's fine.
    if "already installed" in (r.stderr or "").lower():
        return "already installed"
    return f"failed: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown'}"


def _brew_install(tool: Tool) -> str:
    cmd = ["brew", "install", tool.bin]
    if tool.bin.startswith("--cask"):
        cmd = ["brew", "install", "--cask", tool.bin.split()[-1]]
    r = _run(cmd)
    if r.returncode == 0:
        return "installed"
    return f"failed: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown'}"


# --- The catalog ------------------------------------------------------------


def build_catalog() -> list[Tool]:
    """Returns the full tool catalog with installers per distro family."""

    tools: list[Tool] = []

    # Helper to keep the data declarations readable
    def add(key, name, group, desc, bin_, opt_in=False, **installers):
        t = Tool(
            key=key,
            name=name,
            group=group,
            description=desc,
            bin=bin_,
            opt_in=opt_in,
        )
        t.installers = installers
        tools.append(t)

    # ===== RE Core =====
    add(
        "jadx",
        "JADX",
        "RE Core",
        "APK/Dex decompiler to Java source",
        "jadx",
        arch=lambda t: (
            _pacman_install(t, True)
            if _pacman_has(t.bin)
            else _aur_install(t, "paru", False)
            if shutil.which("paru")
            else "manual (AUR)"
        ),
        debian=lambda t: _apt_install(t, True),
        darwin=lambda t: _brew_install(t),
    )
    add(
        "apktool",
        "Apktool",
        "RE Core",
        "APK decode/rebuild + smali",
        "apktool",
        arch=lambda t: _pacman_install(t, True),
        debian=lambda t: _apt_install(t, True),
        darwin=lambda t: _brew_install(t),
    )
    add(
        "dex2jar",
        "dex2jar",
        "RE Core",
        "DEX to JAR converter",
        "dex2jar",
        arch=lambda t: (
            _aur_install(t, "paru", False) if shutil.which("paru") else "manual (AUR)"
        ),
        debian=lambda t: _apt_install(t, True),
        darwin=lambda t: _brew_install(t),
    )
    add(
        "baksmali",
        "baksmali",
        "RE Core",
        "Disassembler for DEX (smali)",
        "baksmali",
        arch=lambda t: (
            _aur_install(t, "paru", False) if shutil.which("paru") else "manual (AUR)"
        ),
        debian=lambda t: _apt_install(t, True),
        darwin=lambda t: _brew_install(t),
    )
    add(
        "smali",
        "smali",
        "RE Core",
        "Assembler for DEX",
        "smali",
        arch=lambda t: (
            _aur_install(t, "paru", False) if shutil.which("paru") else "manual (AUR)"
        ),
        debian=lambda t: _apt_install(t, True),
        darwin=lambda t: _brew_install(t),
    )
    add(
        "frida",
        "Frida tools",
        "RE Core",
        "Dynamic instrumentation (pip)",
        "frida",
        arch=lambda t: _pip_install(t),
        debian=lambda t: _pip_install(t),
        darwin=lambda t: _pip_install(t),
    )
    add(
        "radare2",
        "radare2",
        "RE Core",
        "Native binary analysis framework",
        "r2",
        arch=lambda t: (
            _pacman_install(t, True) if _pacman_has("radare2") else "manual (radare2)"
        ),
        debian=lambda t: _apt_install(t, True),
        darwin=lambda t: _brew_install(t),
    )
    add(
        "binwalk",
        "Binwalk",
        "RE Core",
        "Firmware analysis + extraction",
        "binwalk",
        arch=lambda t: _pacman_install(t, True),
        debian=lambda t: _apt_install(t, True),
        darwin=lambda t: _brew_install(t),
    )
    add(
        "ghidra",
        "Ghidra",
        "RE Core",
        "NSA SRE framework (requires OpenJDK 17+)",
        "ghidra",
        arch=lambda t: (
            _aur_install(t, "paru", False)
            if shutil.which("paru")
            else "manual (download from ghidra-sre.org)"
        ),
        debian=lambda t: "manual (download from ghidra-sre.org — no apt package)",
        darwin=lambda t: "manual (brew cask: 'brew install --cask ghidra')",
    )

    # ===== Auto-included (JDK is required for Ghidra / JADX) =====
    add(
        "openjdk",
        "OpenJDK 17+",
        "Runtime",
        "Java runtime + JDK (required for Ghidra, JADX, apktool)",
        "javac",
        arch=lambda t: (
            _pacman_install(t, True) if _pacman_has("jdk-openjdk") else "manual"
        ),
        debian=lambda t: (
            _apt_install(t, True)
            if _apt_has("openjdk-21-jdk")
            else _apt_install(_subst(t, "openjdk-17-jdk"), True)
        ),
        darwin=lambda t: _brew_install(t),
    )

    # ===== Android =====
    add(
        "adb",
        "Android Platform Tools (adb)",
        "Android",
        "Android Debug Bridge + fastboot",
        "adb",
        arch=lambda t: (
            _pacman_install(t, True) if _pacman_has("android-tools") else "manual"
        ),
        debian=lambda t: _apt_install(t, True) if _apt_has("adb") else "manual",
        darwin=lambda t: _brew_install(_cask_subst(t, "android-platform-tools")),
    )

    # ===== Network =====
    add(
        "mitmproxy",
        "mitmproxy",
        "Network",
        "Interactive HTTPS intercepting proxy",
        "mitmproxy",
        arch=lambda t: _pacman_install(t, True),
        debian=lambda t: _apt_install(t, True),
        darwin=lambda t: _brew_install(t),
    )
    add(
        "wireshark",
        "Wireshark",
        "Network",
        "Packet capture + protocol analysis",
        "wireshark",
        arch=lambda t: (
            _pacman_install(t, True)
            if _pacman_has("wireshark-qt")
            else _pacman_install(_subst(t, "wireshark-cli"), True)
        ),
        debian=lambda t: _apt_install(t, True),
        darwin=lambda t: _brew_install(_cask_subst(t, "wireshark")),
    )

    # ===== Build / runtime =====
    add(
        "git",
        "Git",
        "Build / Runtime",
        "Version control (almost always pre-installed)",
        "git",
        arch=lambda t: (
            _pacman_install(t, True) if not shutil.which("git") else "already installed"
        ),
        debian=lambda t: (
            _apt_install(t, True) if not shutil.which("git") else "already installed"
        ),
        darwin=lambda t: "skip (Xcode CLT ships git)",
    )
    add(
        "python3",
        "Python 3",
        "Build / Runtime",
        "Required runtime for install.py + tooling",
        "python3",
        arch=lambda t: (
            "skip (pre-installed)"
            if shutil.which("python3")
            else _pacman_install(_subst(t, "python"), True)
        ),
        debian=lambda t: (
            "skip (pre-installed)" if shutil.which("python3") else _apt_install(t, True)
        ),
        darwin=lambda t: (
            "skip (pre-installed)" if shutil.which("python3") else _brew_install(t)
        ),
    )
    add(
        "node",
        "Node.js + npm",
        "Build / Runtime",
        "Required for .opencode/ plugin runtime",
        "npm",
        arch=lambda t: _pacman_install(t, True) if _pacman_has("nodejs") else "manual",
        debian=lambda t: _apt_install(t, True) if _apt_has("nodejs") else "manual",
        darwin=lambda t: _brew_install(t),
    )
    add(
        "uv",
        "uv (Python toolchain)",
        "Build / Runtime",
        "Fast Python package manager (drives memini-ai server)",
        "uv",
        arch=lambda t: (
            _aur_install(t, "paru", False) if shutil.which("paru") else _pip_install(t)
        ),
        debian=lambda t: _pip_install(t),
        darwin=lambda t: _brew_install(t),
    )

    # ===== Windows / .NET RE =====
    # revula is not on PyPI — install from source.
    # https://github.com/president-xd/revula
    #
    # OPT-IN: revula is GPL-3.0-or-later (incompatible with our MIT
    # license — we don't ship it, just call into it). It also has ~100
    # thin wrapper tools and a heavy [full] install (angr ~2 GB,
    # semgrep ~250 MB, frida, pwntools, androguard, etc.). Ghidra MCP
    # + radare2-mcp provide 300+ deeper, focused tools. Enable revula
    # only if you specifically need: Android RE workflows, exploit
    # development (ROP chain builder, heap exploitation, libc database),
    # dynamic analysis (GDB/LLDB/Frida adapters), or tshark-based
    # protocol analysis.
    add(
        "revula",
        "revula (MCP server)",
        "RE Core",
        "All-in-one RE MCP server (PE/ELF/Mach-O, YARA, Capa, .NET IL, Frida, GDB, Android, exploit dev) — installed from source",
        "revula",
        opt_in=True,
        arch=lambda t: _git_pip_install(
            "https://github.com/president-xd/revula.git",
            extras="[full]",
        ),
        debian=lambda t: _git_pip_install(
            "https://github.com/president-xd/revula.git",
            extras="[full]",
        ),
        darwin=lambda t: _git_pip_install(
            "https://github.com/president-xd/revula.git",
            extras="[full]",
        ),
    )
    add(
        "diec",
        "diec (Detect It Easy CLI)",
        "RE Core",
        "Identify packer / compiler / cryptor on PE/ELF/Mach-O binaries "
        "(NOTE: no prebuilt Linux binary; Arch and macOS only)",
        "diec",
        arch=lambda t: (
            _pacman_install(_subst(t, "detect-it-easy"), True)
            if _pacman_has("detect-it-easy")
            else "manual (build from github.com/horsicq/Detect-It-Easy)"
        ),
        debian=lambda t: (
            "manual (no apt package; build from "
            "github.com/horsicq/Detect-It-Easy or use the GUI release)"
        ),
        darwin=lambda t: (
            _brew_install(t)
            if shutil.which("brew")
            else "manual (build from github.com/horsicq/Detect-It-Easy)"
        ),
    )
    add(
        "yara",
        "YARA",
        "RE Core",
        "Pattern-based malware identification (YARA rules)",
        "yara",
        arch=lambda t: _pacman_install(t, True) if _pacman_has("yara") else "manual",
        debian=lambda t: _apt_install(t, True) if _apt_has("yara") else "manual",
        darwin=lambda t: _brew_install(t),
    )
    add(
        "pefile",
        "pefile (Python)",
        "RE Core",
        "Python PE file parser library (used by revula, custom scripts)",
        "python3",
        arch=lambda t: _pipx_or_pip_install("pefile"),
        debian=lambda t: _pipx_or_pip_install("pefile"),
        darwin=lambda t: _pipx_or_pip_install("pefile"),
    )
    add(
        "dotnet-sdk",
        ".NET SDK 9+",
        "RE Core",
        ".NET SDK (required for ilspycmd .NET decompiler)",
        "dotnet",
        arch=lambda t: (
            _aur_install(_subst(t, "dotnet-sdk"), "paru", False)
            if shutil.which("paru")
            else "manual (dotnet.microsoft.com/download)"
        ),
        debian=lambda t: (
            "manual (use: wget -qO- https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 9.0)"
            if not _apt_has("dotnet-sdk-9.0")
            else _apt_install(_subst(t, "dotnet-sdk-9.0"), True)
        ),
        darwin=lambda t: _brew_install(_cask_subst(t, "dotnet-sdk")),
    )
    add(
        "ilspycmd",
        "ilspycmd (.NET decompiler)",
        "RE Core",
        "Command-line .NET assembly decompiler (dotnet tool; needs dotnet-sdk first)",
        "ilspycmd",
        arch=lambda t: _dotnet_tool_install("ilspycmd"),
        debian=lambda t: _dotnet_tool_install("ilspycmd"),
        darwin=lambda t: _dotnet_tool_install("ilspycmd"),
    )

    return tools


# --- Tiny helpers used in catalog lambdas ---------------------------------


def _subst(tool: Tool, new_bin: str) -> Tool:
    """Return a shallow copy of the tool with a different package name."""
    return Tool(
        key=tool.key,
        name=tool.name,
        group=tool.group,
        description=tool.description,
        bin=new_bin,
        installers=tool.installers,
    )


def _cask_subst(tool: Tool, cask_name: str) -> Tool:
    return _subst(tool, f"--cask {cask_name}")


def _pacman_has(name: str) -> bool:
    r = subprocess.run(["pacman", "-Si", name], capture_output=True, text=True)
    return r.returncode == 0


def _apt_has(name: str) -> bool:
    r = subprocess.run(["apt-cache", "show", name], capture_output=True, text=True)
    return r.returncode == 0


# --- TUI -------------------------------------------------------------------


def select_tools(tools: list[Tool]) -> list[Tool] | None:
    """Show a checkbox list. Returns the selected tools, or None if cancelled."""
    try:
        import questionary
        from questionary import Choice
    except ImportError:
        warn("'questionary' not installed. Bootstrapping...")
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "questionary"]
        )
        if r.returncode != 0:
            err("Failed to install questionary. Run: pip install --user questionary")
            return None
        import questionary
        from questionary import Choice

    # Group tools under headings
    groups: dict[str, list[Tool]] = {}
    for t in tools:
        groups.setdefault(t.group, []).append(t)

    choices: list[Choice] = []
    for group, group_tools in groups.items():
        choices.append(Choice(f"── {group} ──", value=None, disabled=True))
        for t in group_tools:
            # opt_in=True tools are unchecked by default; the user must
            # explicitly opt into them. The label gets a [opt-in] tag
            # so the user knows why it's unchecked.
            label = f"{t.name:<28}  {t.description}"
            if t.opt_in:
                label += "  [opt-in]"
            choices.append(Choice(title=label, value=t, checked=not t.opt_in))

    selected = questionary.checkbox(
        "Select tools to install (space=toggle, enter=confirm):",
        choices=choices,
        qmark="?",
    ).ask()

    if selected is None:
        return None
    return selected


# --- Status / summary ------------------------------------------------------


@dataclass
class InstallResult:
    tool: Tool
    status: str
    already: bool = False
    manual: bool = False
    failed: bool = False


def install_for_distro(
    tools: list[Tool], distro: Distro, *, assume_yes: bool
) -> list[InstallResult]:
    as_root = os.geteuid() == 0
    results: list[InstallResult] = []

    if as_root and distro.family in ("arch", "debian"):
        warn("Running as root. pacman/apt will not need sudo.")

    if not assume_yes and distro.family in ("arch", "debian") and not as_root:
        info(
            "Sudo may be requested for system packages. Make sure your user has sudo access."
        )

    header(f"Installing {len(tools)} tools on {distro.name}")

    for t in tools:
        if t.is_installed() and not assume_yes:
            results.append(
                InstallResult(tool=t, status="already installed", already=True)
            )
            ok(f"{t.name:<28} already installed")
            continue

        installer = t.installers.get(distro.family)
        if installer is None:
            results.append(
                InstallResult(tool=t, status="no installer for this OS", manual=True)
            )
            warn(f"{t.name:<28} no installer for {distro.name}")
            continue

        info(f"Installing {t.name}…")
        try:
            status = installer(t)
        except subprocess.CalledProcessError as e:
            status = f"failed: {e}"
        except Exception as e:
            status = f"error: {e}"

        r = InstallResult(tool=t, status=status)
        if status.startswith("failed") or status.startswith("error"):
            r.failed = True
            err(f"{t.name:<28} {status}")
        elif status.startswith("manual") or status.startswith("skip"):
            r.manual = True
            warn(f"{t.name:<28} {status}")
        else:
            ok(f"{t.name:<28} {status}")
        results.append(r)

    return results


def print_summary(results: list[InstallResult]) -> None:
    header("Summary")
    installed = [r for r in results if not r.already and not r.failed and not r.manual]
    already = [r for r in results if r.already]
    manual = [r for r in results if r.manual]
    failed = [r for r in results if r.failed]

    print(f"  {color('Installed:', GREEN):<35} {len(installed)}")
    print(f"  {color('Already installed:', CYAN):<35} {len(already)}")
    print(f"  {color('Manual install required:', YELLOW):<35} {len(manual)}")
    print(f"  {color('Failed:', RED):<35} {len(failed)}")

    if manual:
        print()
        warn("The following tools have no package on this platform.")
        warn("See RE_Playground/README.md for manual install instructions:")
        for r in manual:
            print(f"    - {r.tool.name} ({r.tool.bin}): {r.status}")

    if failed:
        print()
        err("The following tools failed to install. Check the output above.")
        for r in failed:
            print(f"    - {r.tool.name}: {r.status}")


# --- Commands --------------------------------------------------------------


def cmd_check(distro: Distro, tools: list[Tool]) -> int:
    header(f"Status check on {distro.name}")
    rows: list[tuple[str, str, str]] = []
    for t in tools:
        if t.is_installed():
            rows.append((t.name, t.bin, color("installed", GREEN)))
        else:
            rows.append((t.name, t.bin, color("missing", YELLOW)))

    name_w = max(len(r[0]) for r in rows)
    bin_w = max(len(r[1]) for r in rows)
    for n, b, s in rows:
        print(f"  {n:<{name_w}}  {b:<{bin_w}}  {s}")

    return 0


def cmd_list(tools: list[Tool]) -> int:
    header("Tool catalog")
    last_group = None
    for t in tools:
        if t.group != last_group:
            print(f"\n  {color(t.group, BOLD)}")
            last_group = t.group
        print(f"    - {t.name:<28} {t.description}  [{color(t.bin, DIM)}]")
    return 0


# --- Entrypoint ------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="install.py",
        description="RE_Playground cross-distro tool installer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--yes", action="store_true", help="Install everything default, no prompts"
    )
    parser.add_argument(
        "--check", action="store_true", help="Show what's already installed, no install"
    )
    parser.add_argument(
        "--list", action="store_true", help="Print the tool catalog and exit"
    )
    args = parser.parse_args()

    print(
        color(
            r"""
 ____
|  _ \ _____   _____ _ __ ___  ___
| |_) / _ \ \ / / _ | '__/ __|/ _ \
|  _ |  __/\ V |  __| |  \__ |  __/
|_|_\_\___| \_/ \___|_|  |___/\___|       _
| ____|_ __   __ _(_)_ __   ___  ___ _ __(_)_ __   ___
|  _| | '_ \ / _` | | '_ \ / _ \/ _ | '__| | '_ \ / _ \
| |___| | | | (_| | | | | |  __|  __| |  | | | | | (_| |
|_____|_| |_|\__, |_|_| |_|\___|\___|_|  |_|_| |_|\__, |
 ____  _     |___/                                |___/
|  _ \| | __ _ _   _  __ _ _ __ ___  _   _ _ __   __| |
| |_) | |/ _` | | | |/ _` | '__/ _ \| | | | '_ \ / _` |
|  __/| | (_| | |_| | (_| | | | (_) | |_| | | | | (_| |
|_|   |_|\__,_|\__, |\__, |_|  \___/ \__,_|_| |_|\__,_|
               |___/ |___/
""",
            CYAN,
        )
    )

    distro = detect_distro()
    if distro is None:
        return 1

    info(f"Detected: {distro.name} ({distro.family})")
    if distro.aur_helper:
        info(f"AUR helper: {distro.aur_helper}")

    tools = build_catalog()

    if args.list:
        return cmd_list(tools)

    if args.check:
        return cmd_check(distro, tools)

    # Pick tools
    if args.yes:
        selected = tools
    else:
        selected = select_tools(tools)
        if selected is None:
            err("Cancelled.")
            return 130
        if not selected:
            warn("Nothing selected. Exiting.")
            return 0

    results = install_for_distro(selected, distro, assume_yes=args.yes)
    print_summary(results)
    return 0 if not any(r.failed for r in results) else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        err("\nInterrupted.")
        sys.exit(130)
