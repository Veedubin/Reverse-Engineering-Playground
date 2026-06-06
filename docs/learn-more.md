# Learn More — Curated Reading List for the RE_Playground Toolkit

> Every link below was checked live in June 2026. The list is biased toward
> **practical, runnable tutorials** over survey articles. We link to the
> upstream project GitHub for every tool so you can always see the source
> of truth and file issues.

---

## Table of Contents

- [Where to find our tools on GitHub](#where-to-find-our-tools-on-github)
- [revula — 116-tool RE MCP server](#revula--116-tool-re-mcp-server)
- [Ghidra + ghidra-mcp](#ghidra--ghidra-mcp)
- [radare2 + r2mcp](#radare2--r2mcp)
- [Frida](#frida)
- [ILSpy / ILSpyMcpServer (.NET)](#ilspy--ilspymcpserver-net)
- [Detect-It-Easy (diec) + D.I.E-MCP](#detect-it-easy-diec--d-ie-mcp)
- [YARA + yara-python](#yara--yara-python)
- [pefile (Python PE parser)](#pefile-python-pe-parser)
- [binwalk (firmware carving)](#binwalk-firmware-carving)
- [JADX + Apktool (Android)](#jadx--apktool-android)
- [Ghidra headless scripting](#ghidra-headless-scripting)
- [RE methodology & theory](#re-methodology--theory)

---

## Where to find our tools on GitHub

These are the upstream repos — bookmark them, star them, file issues.

| Tool | GitHub | What it is |
|------|--------|-----------|
| **revula** | https://github.com/president-xd/revula | 116-tool RE MCP server (PE/ELF/Mach-O, YARA, Capa, .NET IL, Frida, GDB, Android, exploit dev) |
| **Ghidra** | https://github.com/NationalSecurityAgency/ghidra | NSA's SRE framework, 245+ MCP tools via ghidra-mcp |
| **radare2** | https://github.com/radareorg/radare2 | CLI reverse engineering framework |
| **r2mcp** | https://github.com/radareorg/radare2-mcp | MCP server for radare2 |
| **Frida** | https://github.com/frida/frida | Dynamic instrumentation toolkit |
| **ILSpyMcpServer** | https://github.com/bivex/ILSpy-Mcp | .NET decompiler MCP wrapper |
| **ILSpy** | https://github.com/icsharpcode/ILSpy | The underlying .NET decompiler engine |
| **Detect-It-Easy** | https://github.com/horsicq/Detect-It-Easy | Packer / compiler / cryptor detection |
| **D.I.E-MCP** | https://github.com/lazy-importer/D.I.E-MCP | DiE MCP server wrapper |
| **YARA** | https://github.com/VirusTotal/yara | Pattern-matching malware identification |
| **awesome-yara** | https://github.com/InQuest/awesome-yara | Curated list of YARA rules & tools |
| **pefile** | https://github.com/erocarrera/pefile | Python PE parser |
| **binwalk** | https://github.com/ReFirmLabs/binwalk | Firmware / embedded file carver |
| **JADX** | https://github.com/skylot/jadx | APK/Dex decompiler |
| **Apktool** | https://github.com/iBotPeaches/Apktool | APK decode / rebuild + smali |
| **dotfile** | https://github.com/nicpenning/dotnetfile | .NET PE parser (mentioned in Unit42 research) |

---

## revula — 116-tool RE MCP server

> The single most important tool added to RE_Playground. One `pip install` and
> your agents have PE/ELF/Mach-O parsing, YARA scanning, Capa ATT&CK mapping,
> .NET IL disassembly, Frida injection, GDB debugging, ROP chain building, and
> 110 other tools, all addressable through natural language.

- **Repo & docs** — https://github.com/president-xd/revula (start here)
- **Listing on mcpservers.org** — https://mcpservers.org/servers/president-xd/revula
- **Why it matters for AI-driven RE** — https://www.linkedin.com/posts/mohsin-lashari_github-president-xdrevula-a-fully-functional-activity-7438980021345632256-8FWm
- **Reverse engineering with MCP — survey article** —
  https://www.udemy.com/course/ai-mcp-reverse-engineering/ (paid, but the
  syllabus lists 15+ hours of practical MCP-for-RE exercises)
- **Conceptual background: "Using LLMs as a reverse engineering sidekick"** (Cisco Talos, 2025)
  https://blog.talosintelligence.com/using-llm-as-a-reverse-engineering-sidekick/
- **Related: GhidraMCP walkthrough** —
  https://medium.com/@metehanuluocak/ghidramcp-ai-powered-reverse-engineering-made-easy-8b012183acd5
- **Related: ReVa (IDA Pro MCP)** —
  https://github.com/cyberkaida/reverse-engineering-assistant

### How to use it (cheat sheet)

After `pip install revula` and adding the MCP entry to `opencode.json`, your
agents can do things like:

```
Ask the agent: "Analyze /samples/suspicious.exe"
→ agent calls: re_pe_elf, re_strings, re_entropy, re_yara_scan, re_capa_scan
→ agent calls: re_apk_parse (if .apk), re_dex_analyze, re_android_decompile
→ agent returns: hashes, imported functions, suspicious indicators, ATT&CK map
```

For interactive debug: `re_gdb action=start`, `re_gdb action=breakpoint`,
`re_gdb action=continue` — the agent chains them.

---

## Ghidra + ghidra-mcp

- **Upstream** — https://github.com/NationalSecurityAgency/ghidra
- **245-tool ghidra-mcp bridge** — https://github.com/bethington/ghidra-mcp
  (or whatever fork your distro ships; the `ghidra-mcp` PyPI name is the
  standard)
- **Headless analysis tutorial** —
  https://tristanwhite.me/posts/ghidra-headless/ (the `analyzeHeadless`
  binary — same engine our Docker container uses)
- **4-session intro course** —
  https://wrongbaud.github.io/posts/ghidra-training/
- **Low-level Ghidra notes (scripting, decompiler internals)** —
  https://low-level.readthedocs.io/en/latest/reversing/ghidra/
- **PyGhidra (CPython bridge)** — https://pypi.org/project/pyghidra/ and
  https://1337skills.com/cheatsheets/pyghidra/
- **Extracting decompiler output with Python** —
  https://medium.com/tenable-techblog/extracting-ghidra-decompiler-output-with-python-a737e9ed8fce
- **Headless scripts collection** —
  https://github.com/galoget/ghidra-headless-scripts
- **Varonis: "How to Use Ghidra to Reverse Engineer Malware"** —
  https://www.varonis.com/blog/how-to-use-ghidra
- **Jorian Woltjer intro** —
  https://jorianwoltjer.com/blog/p/stories/introduction-to-reverse-engineering-with-ghidra

---

## radare2 + r2mcp

- **Upstream** — https://github.com/radareorg/radare2
- **r2mcp** — https://github.com/radareorg/radare2-mcp
- **Official book (free PDF)** — https://radare.org/get/r2avtokyo-en.pdf
  (Covers winedbg:// plugin for debugging Win32 PE under Wine)
- **Kali Linux r2 page** — https://www.kali.org/tools/radare2/
- **Cutter (GUI front-end for r2)** — https://github.com/rizinorg/cutter
  (the modern fork of Cutter, using rizin)
- **Rizin (community fork of r2)** — https://github.com/rizinorg/rizin

### Win32 PE under Wine (the killer feature)

```bash
# Start a Win32 PE under Wine, get its PID
wine suspicious.exe &
PID=$!

# Attach r2 via the winedbg plugin
r2 -d winedbg://pid=$PID
# now you can disassemble, set breakpoints, etc. inside a Windows binary
# running natively on Linux
```

---

## Frida

- **Upstream** — https://github.com/frida/frida
- **Docs** — https://frida.re/docs/home/
- **Quickstart** — https://frida.re/docs/quickstart/
- **Official handbook (free)** — https://learnfrida.info/
  (covers basic usage, Stalker, CModule, etc.)
- **FuzzySecurity: Frida on Windows (function hooking + frida-trace)** —
  https://fuzzysecurity.com/tutorials/29.html
- **Instrumenting Windows APIs with Frida (WriteFile, etc.)** —
  https://www.ired.team/miscellaneous-reversing-forensics/windows-kernel-internals/instrumenting-windows-apis-with-frida
- **CyberGhost13337 — Windows API hooking walkthrough** —
  https://cyberghost13337.github.io/2023/12/18/frida-for-windows-part1.html
- **Red Team Notes** —
  https://docs.iredteam.cn/miscellaneous-reversing-forensics/windows-kernel-internals/instrumenting-windows-apis-with-frida
- **8ksec: Frida Stalker (instruction tracing)** —
  https://8ksec.io/advanced-frida-usage-part-10-instruction-tracing-using-frida-stalker/
- **Apriorit: Frida for desktop + mobile** —
  https://www.apriorit.com/dev-blog/web-frida-dynamic-analysis
- **Cheat sheet** — https://awakened1712.github.io/hacking/hacking-frida/

### Frida + Win32 PE under Wine (works!)

```bash
# Install frida + wine
pip install frida frida-tools
# Install wine from your distro's package manager

# Start a Win32 PE under Wine
wine target.exe &
TARGET_PID=$!

# Attach
frida -p $TARGET_PID -l hook.js --no-pause
# edit hook.js → save → next call uses new hook. No restart.
```

Caveat: spawn mode (`frida target.exe`) doesn't work for Wine PE directly;
attach mode (`-p $PID`) does. See Frida issue #3339.

---

## ILSpy / ILSpyMcpServer (.NET)

- **Upstream ILSpy** — https://github.com/icsharpcode/ILSpy
- **ILSpyMcpServer (our MCP wrapper)** — https://github.com/bivex/ILSpy-Mcp
- **NuGet package** — https://www.nuget.org/packages/ILSpyMcpServer
- **ilspycmd CLI** — https://www.nuget.org/packages/ilspycmd/
- **ILSpy Linux/macOS install guide** — https://www.en-na.com/tool/ilspy/guide
- **Intro to .NET RE** — https://medium.com/@tr15t4n/intro-to-net-reverse-engineering-c54823b22d6f
- **Decompiling C# on Linux** — https://linuxvox.com/blog/how-to-compile-decompile-and-run-c-code-in-linux/
- **NDepend: 7 .NET decompilers compared** —
  https://blog.ndepend.com/in-the-jungle-of-net-decompilers/
- **Unit 42: dotnetfile (parse .NET PE files in Python)** —
  https://unit42.paloaltonetworks.com/dotnetfile/
- **ConfuserEx deobfuscation workflow** —
  https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/reverse-engineering-dotnet-malware-with-dnspy/SKILL.md

### Quick start

```bash
# Install the .NET SDK (already in install.py)
sudo pacman -S dotnet-sdk   # Arch
# or
brew install --cask dotnet-sdk  # macOS

# Install ilspycmd
dotnet tool install -g ilspycmd
export PATH="$PATH:$HOME/.dotnet/tools"

# Decompile any .NET assembly to C#
ilspycmd suspicious.dll
ilspycmd suspicious.exe
# → prints full C# to stdout, use -p to project-format dump
```

---

## Detect-It-Easy (diec) + D.I.E-MCP

- **Upstream** — https://github.com/horsicq/Detect-It-Easy
- **D.I.E-MCP wrapper** — https://github.com/lazy-importer/D.I.E-MCP
- **Kali package** — https://www.kali.org/tools/detect-it-easy/
- **Tutorial (Malware analysis with DiE)** —
  https://medium.com/@digistam/malware-analysis-with-detect-it-easy-232b9833b18e
- **RedLotus guide** —
  https://itzicehere.gitbook.io/redlotusguide/screensharing-general-knowledge/ninth-section-more-artifact-analysis-for-screensharing/detect-it-easy
- **1337skills cheatsheet** —
  https://1337skills.com/cheatsheets/detect-it-easy/

### CLI quick start

```bash
# Install (Kali/Debian)
sudo apt install detect-it-easy
# or
brew install detect-it-easy
# (on other distros, grab from GitHub releases)

# Identify a binary
diec suspicious.exe
# →  Compiler: Microsoft Visual C/C++ 2019
# →  Linker:    Microsoft Linker 14.0
# →  Packer:    UPX 3.96
# →  Cryptor:   -

# Or use the MCP wrapper
# (add die-mcp to opencode.json, then ask the agent)
# "what packer was used on /samples/target.exe?"
```

---

## YARA + yara-python

- **Upstream** — https://github.com/VirusTotal/yara
- **Docs** — https://yara.readthedocs.io/
- **Awesome YARA list (curated rules)** —
  https://github.com/InQuest/awesome-yara
- **Neo23x0 style guide (industry standard)** —
  https://github.com/Neo23x0/YARA-Style-Guide
- **ReversingLabs: writing detailed YARA rules** —
  https://www.reversinglabs.com/blog/writing-detailed-yara-rules-for-malware-detection
- **TheHGTech beginner → intermediate guide (2026)** —
  https://thehgtech.com/guides/yara-rules-malware-detection.html
- **Complete YARA writing guide (sbytec)** —
  https://www.sbytec.com/blog/yara-guide/
- **Varonis: YARA for threat hunters** —
  https://www.varonis.com/blog/yara-rules
- **Applied Network Defense (paid course, gold standard)** —
  https://www.networkdefense.co/courses/yara/

### Minimal YARA rule

```yara
rule Win32_Packed_UPX
{
    meta:
        author      = "you"
        description = "Detects UPX-packed Win32 PE"
        reference   = "https://github.com/Neo23x0/YARA-Style-Guide"
    strings:
        $upx1 = "UPX!" ascii
        $upx2 = "UPX0" ascii
    condition:
        uint16(0) == 0x5a4d and          // MZ header (PE)
        filesize < 50MB and
        (all of them)
}
```

```bash
# Run
yara -r rules.yar /samples/

# Use the Python binding
python3 -c "import yara; r = yara.compile('rules.yar'); m = r.match('/samples/x.exe'); print(m)"
```

---

## pefile (Python PE parser)

- **Upstream** — https://github.com/erocarrera/pefile
- **PyPI** — https://pypi.org/project/pefile/
- **Docs** — https://pefile.readthedocs.io/
- **DeepWiki overview** — https://deepwiki.com/erocarrera/pefile
- **ForensicITGuy: Rich header hashes with pefile** —
  https://forensicitguy.github.io/rich-header-hashes-with-pefile/
- **Analysing PE files (imports walkthrough)** —
  https://sant-in.medium.com/analysing-pe-files-to-classify-malware-part-i-06ceeebbe717
- **axcheron: PE format manipulation with pefile** —
  https://axcheron.github.io/pe-format-manipulation-with-pefile/
- **Buffer Overflows: exploring PE files** —
  https://bufferoverflows.net/exploring-pe-files-with-python/
- **Detect packers/cryptors (yara + pefile)** —
  https://isleem.medium.com/detect-malware-packers-and-cryptors-with-python-yara-pefile-65bf3c15be378
- **OptimizationCore: imphash in malware analysis** —
  https://www.optimizationcore.com/security/imphash-usage-malware-analysis-categorizing-malware/

### Quick example

```python
import pefile
pe = pefile.PE("/samples/suspicious.exe")

# Hashes
print("MD5:    ", pe.get_imphash())  # import-hash, groups by behavior
print("Entry:  ", hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint))

# Sections
for s in pe.sections:
    print(f"{s.Name.decode().rstrip(chr(0)):<10}  vsize={s.Misc_VirtualSize:<10}  entropy={s.get_entropy():.2f}")

# Imports
if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        print(f"  Imports from {entry.dll.decode()}:")
        for imp in entry.imports:
            print(f"    {imp.name.decode() if imp.name else f'ordinal_{imp.ordinal}'}")
```

---

## binwalk (firmware carving)

- **Upstream** — https://github.com/ReFirmLabs/binwalk
- **Docs** — https://github.com/ReFirmLabs/binwalk/wiki
- **Kali tool page** — https://www.kali.org/tools/binwalk/

```bash
# Quick scan (don't extract, just identify)
binwalk suspicious_firmware.bin

# Recursive extract
binwalk -e suspicious_firmware.bin

# With entropy overlay (find encrypted regions)
binwalk -E suspicious_firmware.bin
```

---

## JADX + Apktool (Android)

- **JADX** — https://github.com/skylot/jadx
- **Apktool** — https://github.com/iBotPeaches/Apktool
- **Frida + Android (`kahlo-mcp`)** — https://github.com/FuzzySecurity/kahlo-mcp
- **Android Skills marketplace entry** — https://mcp.directory/skills/reverse-engineering-tools

---

## Ghidra headless scripting

- **Ghidra's headless analyzer** — https://ghidra-sre.org/InstallationGuide.html
- **Trails of Bits curated skill** — https://lobehub.com/skills/trailofbits-skills-curated-ghidra-headless
- **OFRAK (unified binary analysis framework on top of Ghidra)** —
  https://ofrak.com/docs/user-guide/disassembler-backends/pyghidra.html

### Headless decompile to C

```bash
/opt/ghidra/support/analyzeHeadless \
    /tmp/ghidra-projects my_project \
    -import /samples/suspicious.exe \
    -postScript decompile_all.py \
    -deleteProject
```

Where `decompile_all.py` is one of the scripts in
[galoget/ghidra-headless-scripts](https://github.com/galoget/ghidra-headless-scripts).

---

## RE methodology & theory

- **Awesome Cybersecurity Handbooks (RE chapter)** —
  https://github.com/0xsyr0/Awesome-Cybersecurity-Handbooks/blob/main/handbooks/07_reverse_engineering.md
- **reverseengineering.stackexchange** —
  https://reverseengineering.stackexchange.com/
- **Practical Malware Analysis (the book, online references)** —
  https://nostarch.com/malware
- **Malware Unicorn RE 101 / 102 workshops** —
  https://malwareunicorn.org/workshops
- **Max Kersten on malware analysis** — https://maxkersten.nl/
- **tjl79's malware analysis blog** — https://0xdf.gitlab.io/
- **The Daily Workflow: Reversecore MCP entry** —
  https://thedailyworkflow.com/mcp/server/reversecore-mcp
- **Comparative RE tools table (Ghidra / IDA / Binary Ninja / r2)** —
  https://yen-coder.github.io/Comparison-of-RE-Tools/wiki/Tool-Comparison

---

## How to contribute to this list

PRs welcome at https://github.com/Veedubin/Reverse-Engineering-Playground —
add new entries under the right section with one sentence of context.
Dead links: open an issue with the broken URL.
