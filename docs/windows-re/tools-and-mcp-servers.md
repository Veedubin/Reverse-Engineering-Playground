# Windows Binary Reverse Engineering — Tools & MCP Servers

> Reference compiled 2026-06-06. Covers PE (x86/x64/ARM), .NET, drivers, and resources,
> with focus on what runs on Linux (our deployment target).

---

## TL;DR — What we can do TODAY, without installing anything new

| Task | Tool | Notes |
|------|------|-------|
| Open a `.exe` / `.dll` | **Ghidra** | Auto-detects PE, decompiles to C, full MCP (245 tools) |
| Disassemble x86/x64 PE | **radare2** | `bintype=pe, os=windows` confirmed on real files; radare2-mcp |
| Disassemble + analyze (alt UI) | **rizin** | Drop-in r2 successor, friendlier output |
| Extract strings (incl. UTF-16) | `strings -el` (binutils) | Already installed |
| Read PE sections/imports/exports | **radare2** `iI`, `is`, `iE` | Works without Wine |
| Header walk, hashes, file info | `file`, `objdump -p`, `xxd` | Already installed |
| Find embedded archives/resources | **binwalk** | Already installed |
| Debug a Win32 PE running under Wine | **radare2** with `rwd winedbg://` | Plugin ships with r2 |
| Symbol-level debug (PDB) | **Ghidra** (import PDB) or r2 `idpd` | Free PDB downloader: `pdb_downloader.py` |

For a static RE pass on any random Windows binary, **open it in Ghidra** — it's already
natively cross-platform and the 245-tool MCP surface is already wired into RE_Playground.

---

## New tools to add to `install.py` (when ready)

These are the most useful Windows-specific additions. None of them require a GUI.

### A. `.NET` (C# / VB.NET / F#) assemblies

| Tool | Install | What it does |
|------|---------|--------------|
| **Mono** | apt: `mono-runtime mono-utils mono-devel` pacman: `mono` brew: `mono` | Run .NET Framework apps on Linux; includes `monodis` (IL disassembler) |
| **dotnet SDK 9.0+** | https://dot.net | Required for `ilspycmd` |
| **ilspycmd** | `dotnet tool install -g ilspycmd` | CLI .NET decompiler → C# |
| **AvaloniaILSpy** | https://github.com/icsharpcode/AvaloniaILSpy/releases | GUI .NET browser (Linux AppImage) |
| **de4dot** | https://github.com/de4dot/de4dot | .NET deobfuscator (ConfuserEx, .NET Reactor, etc.) |
| **pefile** | `pip install pefile` | Python PE parser (also a revula dep) |
| **dnlib** | `pip install dnlib` | Read/modify .NET assemblies programmatically |

### B. Static analysis utilities

| Tool | Install | What it does |
|------|---------|--------------|
| **diec** (Detect It Easy CLI) | `apt: detect-it-easy` (Kali), or download from horsicq/Detect-It-Easy | Identify packer / compiler / linker / cryptor |
| **yara** + **yara-python** | `apt: yara python3-yara` | Pattern-based malware identification |
| **ssdeep** | `apt: ssdeep` `pip install ssdeep` | Fuzzy / context-triggered piecewise hashing |
| **tlsh** | `pip install tlsh` | Locality-sensitive similarity hashing |
| **FLOSS** (FireEye) | https://github.com/mandiant/flare-floss | Extract obfuscated strings (stack strings, encoded) |
| **Capa** | https://github.com/mandiant/capa | Map binaries to MITRE ATT&CK techniques |
| **upx-ucl** | `apt: upx-ucl` | Decompress UPX-packed binaries |
| **angr** | `pip install angr` (~2 GB) | Symbolic execution, CFG recovery, vuln scanning |
| **pwntools** | `pip install pwntools` | Exploit dev helpers, ROP gadgets, format strings |

### C. Dynamic analysis

| Tool | Install | What it does |
|------|---------|--------------|
| **wine** | `apt: wine wine64 wine-gecko wine-mono` pacman: `wine` brew: `wine-stable --cask` | Run Win32 PE on Linux (no Win license) |
| **frida** + **frida-tools** | `pip install frida frida-tools` (+ matching frida-server on target) | Dynamic instrumentation; works on Win32 PE under Wine |
| **gdb** | already installed | Use with Wine; Ghidra also has a Wine-debugger bridge |

---

## MCP Servers for Windows RE

| Server | License | Tools | Best for | Install |
|--------|---------|-------|----------|---------|
| **revula** (president-xd/revula) | GPL | **116** | All-in-one malware + multi-format RE | `git clone … && pip install -e ".[full]"` (also Docker) |
| **ILSpyMcpServer** (bivex/ILSpy-Mcp) | MIT | 8 | .NET decompilation via natural language | `dotnet tool install -g ILSpyMcp.Server` |
| **D.I.E-MCP** (lazy-importer/D.I.E-MCP) | MIT | (wraps `diec`) | Packer/compiler detection | needs `diec` binary |
| **Reversecore MCP** (jkim1127/reversecore) | MIT | 5 | Ghidra+r2+YARA wrapper (subset of revula) | `pip install reversecore-mcp` |
| **kahlo-mcp** (FuzzySecurity/kahlo-mcp) | MIT | (Frida) | Android (not Windows) | skip for now |
| **frida-mcp** (dnakov) | MIT | (Frida generic) | Cross-platform Frida | `pip install frida-mcp` |

### Recommended integration order (low → high leverage)

1. **Add `pefile`, `diec`, `yara` to `install.py`** — small Python packages, zero
   configuration, gives the agents cheap "what is this file?" answers.
2. **Add `ILSpyMcpServer`** — only if user does .NET work; one-line `dotnet tool install`,
   big win for CLR analysis.
3. **Add `revula`** — biggest single jump. 116 tools, one Python install, replaces
   what would otherwise be 6+ separate MCPs. Use as the primary "second opinion" /
   cross-format RE backend alongside our existing ghidra-mcp and radare2-mcp.
4. **Add `D.I.E-MCP`** — useful complement to revula; revula already has packer
   detection but D.I.E has the most thorough signature DB.

### Sample opencode.json additions

```jsonc
{
  "mcp": {
    // .NET decompiler — needs dotnet 9 SDK on PATH
    "ilspy-mcp": {
      "type": "stdio",
      "command": "ilspy-mcp",
      "args": []
    },
    // Detect-It-Easy — needs diec binary on PATH
    "die-mcp": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "die_mcp"]   // pip name: iflow-mcp-lazy-importer-die
    },
    // All-in-one RE backend — most useful for PE/ELF/malware
    "revula": {
      "type": "stdio",
      "command": "revula",
      "args": []
    }
  }
}
```

---

## Workflow: triaging a suspicious `.exe`

This is the most common Windows RE task. Using tools we already have + `diec` + `yara`:

```bash
# 1. File type & hashes
file suspicious.exe
sha256sum suspicious.exe

# 2. Header walk + imports
r2 -q -c "iI; iS; ii" suspicious.exe
#   → architecture, sections, imported functions (hints at behaviour)

# 3. Packer / compiler detection
diec suspicious.exe
#   → "UPX 3.96", "MSVC 2022", "Themida", etc.

# 4. YARA scan
yara -r /path/to/rules.yar suspicious.exe

# 5. Open in Ghidra for full decompile
#    (ghidra-mcp: decompile_function, list_imports, etc.)

# 6. If packed → unpack first
upx -d suspicious.exe -o unpacked.exe     # if UPX
#    For other packers: use revula's re_unpack_dynamic (Frida-based)

# 7. If .NET → ILSpyCmd
ilspycmd suspicious.exe
#    or: dotnet tool install -g ilspycmd
```

For **dynamic** analysis of a Win32 PE on Linux:

```bash
# Install wine + frida
sudo pacman -S wine frida            # Arch
sudo apt install wine                # Debian

# Launch the target under Wine
wine suspicious.exe &
TARGET_PID=$!

# Attach Frida (works on Win32 PE under Wine)
frida -p $TARGET_PID -l hook.js --no-pause
```

---

## What we CANNOT do (without a Windows VM)

| Task | Workaround |
|------|-----------|
| Kernel driver RE (.sys) | Use static analysis only. WinDbg requires Windows. |
| ETW / WMI tracing | None on Linux. |
| Signed-driver validation against Microsoft root CA | None. |
| Active Directory / domain-joined testing | Spin up Windows VM (QEMU/KVM). |
| Testing anti-VM / anti-debug tricks that detect Wine | Use a real Windows VM. |
| COM / DCOM RPC live analysis | Spin up Windows VM. |

For everything else (PE/ELF analysis, .NET decompilation, malware static triage,
function-level RE, fuzzy-hash similarity, ATT&CK mapping), the Linux toolchain
above is more than sufficient.

---

## Sources (2026-06-06)

- revula: github.com/president-xd/revula (verified README, 116 tools, GPL, stdio)
- ILSpyMcpServer: github.com/bivex/ILSpy-Mcp + nuget.org/packages/ILSpyMcpServer (MIT, 8 tools)
- D.I.E-MCP: github.com/lazy-importer/D.I.E-MCP (MIT, wraps diec)
- Reversecore: thedailyworkflow.com/mcp/server/reversecore-mcp (MIT, 5 tools)
- r2 + Wine: radare.org/get/r2avtokyo-en.pdf (winedbg:// plugin), john-millikin.com (Ghidra+Wine)
- Frida + Wine: github.com/frida/frida/issues/3339 (works for attach-mode, not spawn-mode without shim)
- ILSpy Linux: github.com/icsharpcode/ILSpy + nuget.org/packages/ilspycmd
- .NET 7 decompilers comparison: blog.ndepend.com/in-the-jungle-of-net-decompilers
- DiE for Linux: github.com/horsicq/Detect-It-Easy, kali.org/tools/detect-it-easy
- Best RE tools 2026: devopsschool.com/blog/top-10-reverse-engineering-tools-in-2025
- ILSpyCmd 10.1.0.8386: nuget.org/packages/ilspycmd
